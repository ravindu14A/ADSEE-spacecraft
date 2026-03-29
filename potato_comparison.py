"""
Potato Diagram Comparison: CRJ-1000 (Baseline) vs CRJ-EXX (Modified)

Generates both potato diagrams using their respective input files and
plots them side-by-side plus overlaid for direct visual comparison.
Also prints a quantitative summary table.

Approach: A single generic build_potato() function is called twice with
different inputs (Task 1 vs Task 2). The loading logic is identical, so
any difference is solely from the engineering changes.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import FormatStrFormatter

# ── Task 1 imports (original CRJ-1000) ──
import Input as ip1
import CG_positions as cg1

# ── Task 2 imports (CRJ-EXX variant) ──
import Input_updated as ip2
import CG_positions_updated as cg2


# =====================================================================
# HELPER
# =====================================================================
def add_mass(current_w, current_cg, added_w, added_cg):
    new_w = current_w + added_w
    if new_w == 0:
        return 0, current_cg
    new_cg = (current_w * current_cg + added_w * added_cg) / new_w
    return new_w, new_cg


# =====================================================================
# GENERIC POTATO BUILDER
# =====================================================================
def build_potato(OEW, X_EOW, MTOW, MAX_FUEL, X_FUEL,
                 MASS_FRONT_CARGO, X_FRONT_CARGO,
                 MASS_AFT_CARGO, X_AFT_CARGO,
                 MASS_PAX, NUM_ROWS, X_ROW_1, ROW_PITCH,
                 X_LEMAC, MAC):
    row_positions = [X_ROW_1 + i * ROW_PITCH for i in range(NUM_ROWS)]

    pa_W = [OEW];  pa_CG = [X_EOW]
    pb_W = [OEW];  pb_CG = [X_EOW]

    # Cargo
    w, c = add_mass(pa_W[-1], pa_CG[-1], MASS_FRONT_CARGO, X_FRONT_CARGO)
    pa_W.append(w); pa_CG.append(c)
    w, c = add_mass(pa_W[-1], pa_CG[-1], MASS_AFT_CARGO, X_AFT_CARGO)
    pa_W.append(w); pa_CG.append(c)
    w, c = add_mass(pb_W[-1], pb_CG[-1], MASS_AFT_CARGO, X_AFT_CARGO)
    pb_W.append(w); pb_CG.append(c)
    w, c = add_mass(pb_W[-1], pb_CG[-1], MASS_FRONT_CARGO, X_FRONT_CARGO)
    pb_W.append(w); pb_CG.append(c)

    # Window seats
    for x in row_positions:
        w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
        pa_W.append(w); pa_CG.append(c)
    for x in reversed(row_positions):
        w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
        pb_W.append(w); pb_CG.append(c)

    # Aisle seats
    for x in row_positions:
        w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
        pa_W.append(w); pa_CG.append(c)
    for x in reversed(row_positions):
        w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
        pb_W.append(w); pb_CG.append(c)

    # Fuel
    f_W = [pa_W[-1]]; f_CG = [pa_CG[-1]]
    for f in np.linspace(0, MAX_FUEL, 40)[1:]:
        fuel = min(f, MTOW - f_W[0])
        if fuel <= 0:
            break
        w, c = add_mass(f_W[0], f_CG[0], fuel, X_FUEL)
        f_W.append(w); f_CG.append(c)

    mac_div = MAC if MAC != 0 else 1.0
    pa_mac = [(c - X_LEMAC) / mac_div for c in pa_CG]
    pb_mac = [(c - X_LEMAC) / mac_div for c in pb_CG]
    f_mac  = [(c - X_LEMAC) / mac_div for c in f_CG]

    all_cg = pa_mac + pb_mac + f_mac

    return {
        "pa_mac": pa_mac, "pa_W": pa_W,
        "pb_mac": pb_mac, "pb_W": pb_W,
        "f_mac": f_mac,   "f_W": f_W,
        "fwd": min(all_cg), "aft": max(all_cg),
        "n_cargo": 3, "n_window": 3 + NUM_ROWS, "n_aisle": 3 + 2 * NUM_ROWS,
    }


# =====================================================================
# BUILD BOTH POTATOES
# =====================================================================
X_LEMAC_1 = ip1.x_LEMACw
MAC_1     = cg1.c_macw
cg1_res   = cg1.calculate_aircraft_cgs(X_LEMAC_1)
X_EOW_1   = cg1_res["from_nose"]["aircraft"]
X_FUEL_1  = cg1_res["from_nose"]["components"]["wing"]

data1 = build_potato(
    OEW=ip1.EOW, X_EOW=X_EOW_1, MTOW=ip1.MTOW,
    MAX_FUEL=ip1.W_fuel, X_FUEL=X_FUEL_1,
    MASS_FRONT_CARGO=ip1.MASS_FRONT_CARGO, X_FRONT_CARGO=ip1.X_FRONT_CARGO,
    MASS_AFT_CARGO=ip1.MASS_AFT_CARGO,     X_AFT_CARGO=ip1.X_AFT_CARGO,
    MASS_PAX=ip1.MASS_PAX, NUM_ROWS=ip1.NUM_ROWS,
    X_ROW_1=ip1.X_ROW_1, ROW_PITCH=ip1.ROW_PITCH,
    X_LEMAC=X_LEMAC_1, MAC=MAC_1,
)

X_LEMAC_2 = ip2.x_LEMACw
MAC_2     = cg2.c_macw
cg2_res   = cg2.calculate_aircraft_cgs(X_LEMAC_2)
X_EOW_2   = cg2_res["from_nose"]["aircraft"]
X_FUEL_2  = cg2_res["from_nose"]["components"]["Wing"]

data2 = build_potato(
    OEW=ip2.EOW, X_EOW=X_EOW_2, MTOW=ip2.MTOW,
    MAX_FUEL=ip2.MAX_ALLOWABLE_FUEL_EXX, X_FUEL=X_FUEL_2,
    MASS_FRONT_CARGO=ip2.MASS_FRONT_CARGO, X_FRONT_CARGO=ip2.X_FRONT_CARGO,
    MASS_AFT_CARGO=ip2.MASS_AFT_CARGO,     X_AFT_CARGO=ip2.X_AFT_CARGO,
    MASS_PAX=ip2.MASS_PAX, NUM_ROWS=ip2.NUM_ROWS,
    X_ROW_1=ip2.X_ROW_1, ROW_PITCH=ip2.ROW_PITCH,
    X_LEMAC=X_LEMAC_2, MAC=MAC_2,
)


# =====================================================================
# SHARED PROFESSIONAL STYLE
# =====================================================================
def apply_style():
    mpl.rcParams.update({
        'font.family': 'serif',
        'font.size': 11,
        'axes.labelsize': 13,
        'axes.titlesize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 8.5,
        'figure.dpi': 120,
    })

COL_CARGO = '#1B9E77'
COL_WIN   = '#D95F02'
COL_AISLE = '#7570B3'
COL_FUEL  = '#2171B5'
COL_LIMIT = '#E41A1C'


def _draw_potato(ax, d, title, oew, mtow):
    """Draw a single potato on an axes with the professional style."""
    n_c, n_w, n_a = d["n_cargo"], d["n_window"], d["n_aisle"]
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))

    # Path A (solid)
    ax.plot(d["pa_mac"][:n_c], d["pa_W"][:n_c],
            color=COL_CARGO, marker='s', ms=5, lw=1.8, label='Cargo (fwd→aft)', zorder=3)
    ax.plot(d["pa_mac"][n_c-1:n_w], d["pa_W"][n_c-1:n_w],
            color=COL_WIN, marker='o', ms=3.5, lw=1.4, label='Window pax', zorder=3)
    ax.plot(d["pa_mac"][n_w-1:n_a], d["pa_W"][n_w-1:n_a],
            color=COL_AISLE, marker='o', ms=3.5, lw=1.4, label='Aisle pax', zorder=3)

    # Path B (dashed)
    ax.plot(d["pb_mac"][:n_c], d["pb_W"][:n_c],
            color=COL_CARGO, marker='s', ms=5, lw=1.8, ls='--', zorder=3)
    ax.plot(d["pb_mac"][n_c-1:n_w], d["pb_W"][n_c-1:n_w],
            color=COL_WIN, marker='o', ms=3.5, lw=1.4, ls='--', zorder=3)
    ax.plot(d["pb_mac"][n_w-1:n_a], d["pb_W"][n_w-1:n_a],
            color=COL_AISLE, marker='o', ms=3.5, lw=1.4, ls='--', zorder=3)

    # Fuel
    ax.plot(d["f_mac"], d["f_W"], color=COL_FUEL, lw=3,
            solid_capstyle='round', label='Fuel loading', zorder=4)

    # OEW dot
    ax.scatter([d["pa_mac"][0]], [oew], color='black', s=80, zorder=6,
               edgecolors='white', linewidths=1)

    # CG limits
    ax.axvline(x=d["fwd"], color='grey', ls='--', lw=0.8, alpha=0.5)
    ax.axvline(x=d["aft"], color='grey', ls='--', lw=0.8, alpha=0.5)

    # MTOW
    ax.axhline(y=mtow, color=COL_LIMIT, ls='--', lw=1.3, alpha=0.6)
    ax.text(d["aft"] + 0.01, mtow + 200, f'MTOW', color=COL_LIMIT,
            fontsize=8, fontweight='bold')

    ax.set_title(title, fontweight='bold', pad=10)
    ax.set_xlabel(r'$x_{\mathrm{cg}}\;/\;\mathrm{MAC}$')
    leg = ax.legend(loc='upper left', frameon=True, fancybox=False,
                    edgecolor='#CCC', framealpha=0.95)
    leg.get_frame().set_linewidth(0.5)
    ax.grid(True, which='major', ls='-', lw=0.4, color='#D0D0D0')
    ax.minorticks_on()
    ax.grid(True, which='minor', ls=':', lw=0.25, color='#E8E8E8')
    for sp in ax.spines.values():
        sp.set_linewidth(0.5)
        sp.set_color('#666')


# =====================================================================
# QUANTITATIVE COMPARISON
# =====================================================================
def print_comparison():
    MZFW_1 = ip1.EOW + ip1.W_pax_luggage + ip1.MASS_FRONT_CARGO + ip1.MASS_AFT_CARGO
    MZFW_2 = ip2.MZFW_EXX
    pax1, pax2 = ip1.NUM_ROWS * 4, ip2.NUM_ROWS * 4
    r1 = (data1["aft"] - data1["fwd"]) * 100
    r2 = (data2["aft"] - data2["fwd"]) * 100

    print("\n" + "=" * 80)
    print(" " * 15 + "POTATO DIAGRAM COMPARISON  —  CRJ-1000 vs CRJ-EXX")
    print("=" * 80)
    print(f"{'Parameter':<35} | {'CRJ-1000':>15} | {'CRJ-EXX':>15} | {'Delta':>10}")
    print("-" * 80)

    rows = [
        ("OEW (kg)",                    ip1.EOW,             ip2.EOW),
        ("MTOW (kg)",                   ip1.MTOW,            ip2.MTOW),
        ("MZFW (kg)",                   MZFW_1,              MZFW_2),
        ("Max Fuel (kg)",               ip1.W_fuel,          ip2.MAX_ALLOWABLE_FUEL_EXX),
        ("Passengers",                  pax1,                pax2),
        ("Passenger Rows",              ip1.NUM_ROWS,        ip2.NUM_ROWS),
        ("Total Pax Weight (kg)",       pax1*ip1.MASS_PAX,   pax2*ip2.MASS_PAX),
        ("Front Cargo Mass (kg)",       ip1.MASS_FRONT_CARGO, ip2.MASS_FRONT_CARGO),
        ("Aft Cargo Mass (kg)",         ip1.MASS_AFT_CARGO,  ip2.MASS_AFT_CARGO),
        ("Front Cargo CG (m)",          ip1.X_FRONT_CARGO,   ip2.X_FRONT_CARGO),
        ("Aft Cargo CG (m)",            ip1.X_AFT_CARGO,     ip2.X_AFT_CARGO),
        ("Fuel CG (m)",                 X_FUEL_1,            X_FUEL_2),
        ("EOW CG from nose (m)",        X_EOW_1,             X_EOW_2),
        ("EOW CG (% MAC)",
         (X_EOW_1-X_LEMAC_1)/MAC_1*100, (X_EOW_2-X_LEMAC_2)/MAC_2*100),
        ("Most FWD CG (% MAC)",         data1["fwd"]*100,    data2["fwd"]*100),
        ("Most AFT CG (% MAC)",         data1["aft"]*100,    data2["aft"]*100),
        ("CG Excursion (% MAC)",        r1,                  r2),
    ]

    for label, v1, v2 in rows:
        delta = v2 - v1
        sign = "+" if delta >= 0 else ""
        print(f"  {label:<33} | {v1:>15.2f} | {v2:>15.2f} | {sign}{delta:>9.2f}")

    print("=" * 80)
    envelope_word = "wider" if r2 > r1 else "narrower"
    print(f"\n  The EXX envelope is {envelope_word} ({r2:.1f}% vs {r1:.1f}% MAC).\n")


# =====================================================================
# SIDE-BY-SIDE PLOT
# =====================================================================
def plot_comparison():
    apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), sharey=True)
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('#FAFAFA')
    ax2.set_facecolor('#FAFAFA')

    y_lo = min(ip1.EOW, ip2.EOW) - 1500
    y_hi = ip1.MTOW + 2500

    _draw_potato(ax1, data1, 'CRJ-1000  (Baseline — Task 1)', ip1.EOW, ip1.MTOW)
    _draw_potato(ax2, data2, 'CRJ-EXX  (Modified — Task 2)',  ip2.EOW, ip2.MTOW)

    ax1.set_ylim(y_lo, y_hi)
    ax2.set_ylim(y_lo, y_hi)
    ax1.set_ylabel('Aircraft Mass  (kg)')

    fig.suptitle('Potato Diagram Comparison — CRJ-1000 vs CRJ-EXX',
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


# =====================================================================
# OVERLAY PLOT
# =====================================================================
def plot_overlay():
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#FAFAFA')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))

    n1, n2 = data1["n_aisle"], data2["n_aisle"]

    # CRJ-1000 (blue, lighter)
    ax.fill_betweenx(data1["pa_W"][:n1], data1["pa_mac"][:n1],
                     data1["pb_mac"][:n1], color='#2171B5', alpha=0.10,
                     label='CRJ-1000 envelope')
    ax.plot(data1["pa_mac"][:n1], data1["pa_W"][:n1],
            color='#2171B5', alpha=0.4, lw=1.8)
    ax.plot(data1["pb_mac"][:n1], data1["pb_W"][:n1],
            color='#2171B5', alpha=0.4, lw=1.8, ls='--')
    ax.plot(data1["f_mac"], data1["f_W"],
            color='#2171B5', alpha=0.5, lw=2.5)

    # CRJ-EXX (orange, bolder)
    ax.fill_betweenx(data2["pa_W"][:n2], data2["pa_mac"][:n2],
                     data2["pb_mac"][:n2], color='#D95F02', alpha=0.10,
                     label='CRJ-EXX envelope')
    ax.plot(data2["pa_mac"][:n2], data2["pa_W"][:n2],
            color='#D95F02', lw=1.8)
    ax.plot(data2["pb_mac"][:n2], data2["pb_W"][:n2],
            color='#D95F02', lw=1.8, ls='--')
    ax.plot(data2["f_mac"], data2["f_W"],
            color='#D95F02', lw=2.5, alpha=0.8)

    # OEW dots
    ax.scatter([data1["pa_mac"][0]], [ip1.EOW], color='#2171B5', s=100,
               zorder=5, edgecolors='white', label=f'CRJ-1000 OEW ({ip1.EOW:,} kg)')
    ax.scatter([data2["pa_mac"][0]], [ip2.EOW], color='#D95F02', s=100,
               zorder=5, edgecolors='white', label=f'CRJ-EXX OEW ({ip2.EOW:,.0f} kg)')

    # MTOW
    ax.axhline(y=ip1.MTOW, color=COL_LIMIT, ls='--', lw=1.3, alpha=0.6)
    ax.text(0.01, ip1.MTOW + 200, 'MTOW', color=COL_LIMIT,
            fontsize=9, fontweight='bold', transform=ax.get_yaxis_transform())

    ax.set_ylim(min(ip1.EOW, ip2.EOW) - 1500, ip1.MTOW + 2500)
    ax.set_title('Overlaid Potato Diagrams — CRJ-1000 vs CRJ-EXX',
                  fontsize=15, fontweight='bold', pad=14)
    ax.set_xlabel(r'$x_{\mathrm{cg}}\;/\;\mathrm{MAC}$')
    ax.set_ylabel('Aircraft Mass  (kg)')
    leg = ax.legend(loc='upper left', frameon=True, fancybox=False,
                    edgecolor='#CCC', framealpha=0.95)
    leg.get_frame().set_linewidth(0.5)
    ax.grid(True, which='major', ls='-', lw=0.4, color='#D0D0D0')
    ax.minorticks_on()
    ax.grid(True, which='minor', ls=':', lw=0.25, color='#E8E8E8')
    for sp in ax.spines.values():
        sp.set_linewidth(0.5)
        sp.set_color('#666')

    plt.tight_layout()
    plt.show()


# =====================================================================
if __name__ == '__main__':
    print_comparison()
    plot_comparison()
    plot_overlay()
#hiii