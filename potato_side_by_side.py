import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import FormatStrFormatter
import Input as ip1
import CG_positions as cg1
import Input_updated as ip2
import CG_positions_updated as cg2

def add_mass(current_w, current_cg, added_w, added_cg):
    new_w = current_w + added_w
    if new_w == 0: return 0, current_cg
    new_cg = (current_w * current_cg + added_w * added_cg) / new_w
    return new_w, new_cg

def build_potato(OEW, X_EOW, MTOW, MAX_FUEL, X_FUEL,
                 MASS_FRONT_CARGO, X_FRONT_CARGO,
                 MASS_AFT_CARGO, X_AFT_CARGO,
                 MASS_PAX, NUM_ROWS, X_ROW_1, ROW_PITCH,
                 X_LEMAC, MAC):
    row_positions = [X_ROW_1 + i * ROW_PITCH for i in range(NUM_ROWS)]
    pa_W, pa_CG = [OEW], [X_EOW]
    pb_W, pb_CG = [OEW], [X_EOW]

    w, c = add_mass(pa_W[-1], pa_CG[-1], MASS_FRONT_CARGO, X_FRONT_CARGO)
    pa_W.append(w); pa_CG.append(c)
    w, c = add_mass(pa_W[-1], pa_CG[-1], MASS_AFT_CARGO, X_AFT_CARGO)
    pa_W.append(w); pa_CG.append(c)
    w, c = add_mass(pb_W[-1], pb_CG[-1], MASS_AFT_CARGO, X_AFT_CARGO)
    pb_W.append(w); pb_CG.append(c)
    w, c = add_mass(pb_W[-1], pb_CG[-1], MASS_FRONT_CARGO, X_FRONT_CARGO)
    pb_W.append(w); pb_CG.append(c)

    for x in row_positions:
        w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
        pa_W.append(w); pa_CG.append(c)
    for x in reversed(row_positions):
        w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
        pb_W.append(w); pb_CG.append(c)

    for x in row_positions:
        w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
        pa_W.append(w); pa_CG.append(c)
    for x in reversed(row_positions):
        w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
        pb_W.append(w); pb_CG.append(c)

    f_W, f_CG = [pa_W[-1]], [pa_CG[-1]]
    for f in np.linspace(0, MAX_FUEL, 40)[1:]:
        fuel = min(f, MTOW - f_W[0])
        if fuel <= 0: break
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

X_LEMAC_1 = ip1.x_LEMACw
MAC_1     = cg1.c_macw
cg1_res   = cg1.calculate_aircraft_cgs(X_LEMAC_1)
data1 = build_potato(ip1.EOW, cg1_res["from_nose"]["aircraft"], ip1.MTOW, ip1.W_fuel, cg1_res["from_nose"]["components"]["wing"], ip1.MASS_FRONT_CARGO, ip1.X_FRONT_CARGO, ip1.MASS_AFT_CARGO, ip1.X_AFT_CARGO, ip1.MASS_PAX, ip1.NUM_ROWS, ip1.X_ROW_1, ip1.ROW_PITCH, X_LEMAC_1, MAC_1)

X_LEMAC_2 = ip2.x_LEMACw
MAC_2     = cg2.c_macw
cg2_res   = cg2.calculate_aircraft_cgs(X_LEMAC_2)
data2 = build_potato(ip2.EOW, cg2_res["from_nose"]["aircraft"], ip2.MTOW, ip2.MAX_ALLOWABLE_FUEL_EXX, cg2_res["from_nose"]["components"]["Wing"], ip2.MASS_FRONT_CARGO, ip2.X_FRONT_CARGO, ip2.MASS_AFT_CARGO, ip2.X_AFT_CARGO, ip2.MASS_PAX, ip2.NUM_ROWS, ip2.X_ROW_1, ip2.ROW_PITCH, X_LEMAC_2, MAC_2)

def plot_neat_comparison():
    mpl.rcParams.update({'font.family': 'serif', 'font.size': 13, 'axes.labelsize': 15, 'axes.titlesize': 16, 'figure.dpi': 120})
    # Make the entire figure larger
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9.5), sharey=True)
    fig.patch.set_facecolor('white')
    COL_CARGO, COL_WIN, COL_AISLE, COL_FUEL, COL_LIMIT = '#1B9E77', '#D95F02', '#7570B3', '#2171B5', '#E41A1C'

    def draw_ax(ax, d, title, oew, mtow):
        ax.set_facecolor('#FAFAFA')
        n_c, n_w, n_a = d["n_cargo"], d["n_window"], d["n_aisle"]
        ax.plot(d["pa_mac"][:n_c], d["pa_W"][:n_c], color=COL_CARGO, marker='s', ms=5, lw=2.2, label='Cargo (fwd→aft)')
        ax.plot(d["pa_mac"][n_c-1:n_w], d["pa_W"][n_c-1:n_w], color=COL_WIN, marker='o', ms=4.0, lw=1.8, label='Window pax')
        ax.plot(d["pa_mac"][n_w-1:n_a], d["pa_W"][n_w-1:n_a], color=COL_AISLE, marker='o', ms=4.0, lw=1.8, label='Aisle pax')
        ax.plot(d["pb_mac"][:n_c], d["pb_W"][:n_c], color=COL_CARGO, marker='s', ms=5, lw=2.2, ls='--')
        ax.plot(d["pb_mac"][n_c-1:n_w], d["pb_W"][n_c-1:n_w], color=COL_WIN, marker='o', ms=4.0, lw=1.8, ls='--')
        ax.plot(d["pb_mac"][n_w-1:n_a], d["pb_W"][n_w-1:n_a], color=COL_AISLE, marker='o', ms=4.0, lw=1.8, ls='--')
        ax.plot(d["f_mac"], d["f_W"], color=COL_FUEL, lw=3.5, label='Fuel loading')
        
        # OEW Point
        ax.scatter([d["pa_mac"][0]], [oew], color='black', s=100, zorder=6, edgecolors='white', linewidths=1.5)
        lbl = f'OEW = {oew:,.0f} kg' if '1000' in title else f'OEW+Batt = {oew:,.0f} kg'
        # Safely align left and nudge slightly right of the point to avoid any bounding box clipping!
        ax.text(d["pa_mac"][0] + 0.015, oew - 400, lbl, color='black', fontsize=11, fontweight='bold', ha='left', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))
        
        # MZFW Line
        mzfw = d["pa_W"][-1]
        ax.axhline(mzfw, color='#555555', ls='--', lw=1.8, alpha=0.6)
        # Safely align left at the FWD limit to prevent any axis-spanning bounding boxes!
        ax.text(d["fwd"], mzfw + 250, f' MZFW = {mzfw:,.0f} kg', color='#444444', fontsize=11, fontweight='bold', ha='left')
        
        # MTOW Line
        ax.axhline(mtow, color=COL_LIMIT, ls='--', lw=1.8, alpha=0.6)
        ax.text(d["fwd"], mtow + 250, f' MTOW = {mtow:,.0f} kg', color=COL_LIMIT, fontsize=11, fontweight='bold', ha='left')

        ax.set_title(title, fontweight='bold', pad=14)
        ax.set_xlabel(r'$x_{\mathrm{cg}}\;/\;\mathrm{MAC}$')
        ax.grid(True, ls='-', lw=0.4, color='#D0D0D0')
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        ax.axvline(d["fwd"], color='grey', ls='--', lw=1.0, alpha=0.5)
        ax.axvline(d["aft"], color='grey', ls='--', lw=1.0, alpha=0.5)

    draw_ax(ax1, data1, 'CRJ-1000', ip1.EOW, ip1.MTOW)
    draw_ax(ax2, data2, 'CRJ-EXX', ip2.EOW, ip2.MTOW)

    ax1.set_ylim(min(ip1.EOW, ip2.EOW) - 1500, ip1.MTOW + 2500)
    ax1.set_ylabel('Aircraft Mass (kg)', labelpad=15)

    plt.subplots_adjust(bottom=0.08, top=0.94) # Tighter layout after removing the legend
    plt.show()

if __name__ == '__main__':
    plot_neat_comparison()
