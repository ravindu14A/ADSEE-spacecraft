import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import Input_updated as ip
import CG_positions_updated as cg


def add_mass(current_w, current_cg, added_w, added_cg):
    new_w = current_w + added_w
    if new_w == 0:
        return 0, current_cg
    new_cg = ((current_w * current_cg) + (added_w * added_cg)) / new_w
    return new_w, new_cg


def calculate_cg_limits(X_OEW, X_LEMAC, X_FUEL, plot=False):
    CG_MARGIN = 0.05

    OEW = ip.EOW
    MAC = cg.c_macw
    MTOW = ip.MTOW
    MAX_FUEL = ip.W_fuel

    MASS_PAX = ip.MASS_PAX
    MASS_FRONT_CARGO = ip.MASS_FRONT_CARGO
    X_FRONT_CARGO = ip.X_FRONT_CARGO
    MASS_AFT_CARGO = ip.MASS_AFT_CARGO
    X_AFT_CARGO = ip.X_AFT_CARGO

    NUM_ROWS = ip.NUM_ROWS
    X_ROW_1 = ip.X_ROW_1
    ROW_PITCH = ip.ROW_PITCH

    row_positions = [X_ROW_1 + (i * ROW_PITCH) for i in range(NUM_ROWS)]

    pa_W, pa_CG = [OEW], [X_OEW]
    pb_W, pb_CG = [OEW], [X_OEW]

    # Cargo Loop
    for m, x in [(MASS_FRONT_CARGO, X_FRONT_CARGO), (MASS_AFT_CARGO, X_AFT_CARGO)]:
        w, c = add_mass(pa_W[-1], pa_CG[-1], m, x)
        pa_W.append(w)
        pa_CG.append(c)
    for m, x in [(MASS_AFT_CARGO, X_AFT_CARGO), (MASS_FRONT_CARGO, X_FRONT_CARGO)]:
        w, c = add_mass(pb_W[-1], pb_CG[-1], m, x)
        pb_W.append(w)
        pb_CG.append(c)

    # Window Seats Loop
    for x in row_positions:
        w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
        pa_W.append(w)
        pa_CG.append(c)
    for x in reversed(row_positions):
        w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
        pb_W.append(w)
        pb_CG.append(c)

    # Aisle Seats Loop
    for x in row_positions:
        w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
        pa_W.append(w)
        pa_CG.append(c)
    for x in reversed(row_positions):
        w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
        pb_W.append(w)
        pb_CG.append(c)

    # Fuel Loading
    f_W = [pa_W[-1]]
    f_CG = [pa_CG[-1]]

    for f in np.linspace(0, MAX_FUEL, 40)[1:]:
        if f_W[0] + f <= MTOW:
            w, c = add_mass(f_W[0], f_CG[0], f, X_FUEL)
            f_W.append(w)
            f_CG.append(c)
        else:
            w, c = add_mass(f_W[0], f_CG[0], MTOW - f_W[0], X_FUEL)
            f_W.append(w)
            f_CG.append(c)
            break

    mac_divisor = MAC if MAC != 0 else 1

    pa_mac = [((c - X_LEMAC) / mac_divisor) for c in pa_CG]
    pb_mac = [((c - X_LEMAC) / mac_divisor) for c in pb_CG]
    f_mac = [((c - X_LEMAC) / mac_divisor) for c in f_CG]

    all_cg_mac = pa_mac + pb_mac + f_mac

    most_fwd_cg = min(all_cg_mac)
    most_aft_cg = max(all_cg_mac)

    fwd_limit_with_margin = most_fwd_cg - CG_MARGIN
    aft_limit_with_margin = most_aft_cg + CG_MARGIN

    if plot:
        print(f"--- CG LIMITS SUMMARY ---")
        print(f"Most Forward CG:      {most_fwd_cg:.4f} MAC")
        print(f"Most Aft CG:          {most_aft_cg:.4f} MAC")
        print(f"FWD Limit w/ Margin:  {fwd_limit_with_margin:.4f} MAC")
        print(f"AFT Limit w/ Margin:  {aft_limit_with_margin:.4f} MAC\n")

        # Index helpers for plotting segments
        n_cargo = 3
        n_win   = n_cargo + NUM_ROWS
        n_aisle = n_win + NUM_ROWS

        # ── Professional Plot Style ──
        import matplotlib as mpl
        mpl.rcParams.update({
            'font.family': 'serif',
            'font.size': 11,
            'axes.labelsize': 13,
            'axes.titlesize': 15,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 9,
            'figure.dpi': 120,
        })

        fig, ax = plt.subplots(figsize=(11, 7.5))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('#FAFAFA')
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        # ── Colour palette (academic / TU Delft inspired) ──
        COL_CARGO = '#1B9E77'   # teal
        COL_WIN   = '#D95F02'   # burnt orange
        COL_AISLE = '#7570B3'   # muted purple
        COL_FUEL  = '#2171B5'   # blue
        COL_LIMIT = '#E41A1C'   # red

        # ── Path A (solid — front-to-back) ──
        ax.plot(pa_mac[:n_cargo], pa_W[:n_cargo],
                color=COL_CARGO, marker='s', ms=5, lw=1.8,
                label='Cargo (fwd → aft)', zorder=3)
        ax.plot(pa_mac[n_cargo-1:n_win], pa_W[n_cargo-1:n_win],
                color=COL_WIN, marker='o', ms=3.5, lw=1.4,
                label='Window pax (fwd → aft)', zorder=3)
        ax.plot(pa_mac[n_win-1:n_aisle], pa_W[n_win-1:n_aisle],
                color=COL_AISLE, marker='o', ms=3.5, lw=1.4,
                label='Aisle pax (fwd → aft)', zorder=3)

        # ── Path B (dashed — back-to-front) ──
        ax.plot(pb_mac[:n_cargo], pb_W[:n_cargo],
                color=COL_CARGO, marker='s', ms=5, lw=1.8, ls='--', zorder=3)
        ax.plot(pb_mac[n_cargo-1:n_win], pb_W[n_cargo-1:n_win],
                color=COL_WIN, marker='o', ms=3.5, lw=1.4, ls='--', zorder=3)
        ax.plot(pb_mac[n_win-1:n_aisle], pb_W[n_win-1:n_aisle],
                color=COL_AISLE, marker='o', ms=3.5, lw=1.4, ls='--', zorder=3)

        # ── Fuel loading ──
        ax.plot(f_mac, f_W, color=COL_FUEL, lw=3, solid_capstyle='round',
                label='Fuel loading', zorder=4)

        # ── OEW marker ──
        ax.scatter([pa_mac[0]], [OEW], color='black', s=100, zorder=6,
                   edgecolors='white', linewidths=1.2)
        ax.axvline(x=fwd_limit_with_margin, color=COL_LIMIT, ls='-', lw=1.5, alpha=0.7,
                   label=f'CG limits ± {CG_MARGIN:.0%} MAC')
        ax.axvline(x=aft_limit_with_margin, color=COL_LIMIT, ls='-', lw=1.5, alpha=0.7)

        # Calculated CG extremes (thin dashed)
        ax.axvline(x=most_fwd_cg, color='grey', ls='--', lw=0.8, alpha=0.5)
        ax.axvline(x=most_aft_cg, color='grey', ls='--', lw=0.8, alpha=0.5)

        # ── MTOW line ──
        ax.axhline(y=MTOW, color=COL_LIMIT, ls='--', lw=1.5, alpha=0.6)
        ax.text(ax.get_xlim()[0] + 0.005 if ax.get_xlim()[0] != 0 else most_fwd_cg,
                MTOW + 200, f'MTOW = {MTOW:,.0f} kg',
                color=COL_LIMIT, fontsize=9, fontweight='bold')

        # ── Axes ──
        ax.set_ylim(OEW - 1200, MTOW + 2500)
        ax.set_title('CRJ-EXX — Loading Envelope (Potato Diagram)',
                      fontweight='bold', pad=14)
        ax.set_xlabel(r'$x_{\mathrm{cg}}\;/\;\mathrm{MAC}$')
        ax.set_ylabel('Aircraft Mass  (kg)')

        # ── Legend ──
        leg = ax.legend(loc='upper left', frameon=True, fancybox=False,
                        edgecolor='#CCCCCC', framealpha=0.95)
        leg.get_frame().set_linewidth(0.6)

        # ── Grid ──
        ax.grid(True, which='major', ls='-', lw=0.4, color='#D0D0D0')
        ax.minorticks_on()
        ax.grid(True, which='minor', ls=':', lw=0.25, color='#E8E8E8')

        # ── Spine styling ──
        for spine in ax.spines.values():
            spine.set_linewidth(0.6)
            spine.set_color('#666666')

        plt.tight_layout()
        plt.show()

    return most_fwd_cg, most_aft_cg, fwd_limit_with_margin, aft_limit_with_margin


if __name__ == '__main__':
    # Pull the dictionary using your updated module name
    cg_data_from_nose = cg.calculate_aircraft_cgs(ip.x_LEMACw)["from_nose"]

    # Extract the required values
    X_OEW_CURRENT = cg_data_from_nose["aircraft"]
    # Updated to match the capitalized key in your EXX variant dictionary
    X_WING_CURRENT = cg_data_from_nose["components"]["Wing"]
    X_LEMAC_CURRENT = ip.x_LEMACw

    # Run the function, passing the wing CG as the fuel CG
    fwd, aft, fwd_margin, aft_margin = calculate_cg_limits(
        X_OEW=X_OEW_CURRENT,
        X_LEMAC=X_LEMAC_CURRENT,
        X_FUEL=X_WING_CURRENT,
        plot=True
    )