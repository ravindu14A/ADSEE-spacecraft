import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import Input as ip
import CG_positions as cg


def add_mass(current_w, current_cg, added_w, added_cg):
    """Helper function to calculate new weight and CG."""
    new_w = current_w + added_w

    # Safeguard against division by zero
    if new_w == 0:
        return 0, current_cg

    new_cg = ((current_w * current_cg) + (added_w * added_cg)) / new_w
    return new_w, new_cg


def calculate_cg_limits(X_OEW, X_LEMAC, X_FUEL, plot=False):
    """
    Calculates the most forward and aft CG limits (with and without margins).
    Optionally plots the potato diagram and prints the summary.
    """
    # --- 1. CONFIGURATION & DATA GATHERING ---
    CG_MARGIN = 0.05  # Safety margin for CG limits (e.g., 0.05 = 5% MAC)

    # Aircraft physical data
    OEW = ip.EOW
    MAC = cg.c_macw

    # Operational limits
    MTOW = ip.MTOW
    MAX_FUEL = ip.W_fuel
    # X_FUEL is passed directly into the function arguments now

    # Payload definitions
    MASS_PAX = ip.MASS_PAX
    MASS_FRONT_CARGO = ip.MASS_FRONT_CARGO
    X_FRONT_CARGO = ip.X_FRONT_CARGO
    MASS_AFT_CARGO = ip.MASS_AFT_CARGO
    X_AFT_CARGO = ip.X_AFT_CARGO

    # Cabin rows
    NUM_ROWS = ip.NUM_ROWS
    X_ROW_1 = ip.X_ROW_1
    ROW_PITCH = ip.ROW_PITCH

    row_positions = [X_ROW_1 + (i * ROW_PITCH) for i in range(NUM_ROWS)]

    # --- 2. GENERATE COORDINATES ---
    pa_W = [OEW]
    pa_CG = [X_OEW]
    pb_W = [OEW]
    pb_CG = [X_OEW]

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
    if MTOW <= 0 and plot:
        print("\nCRITICAL WARNING: MTOW is zero or negative. Please check Input.py!\n")

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

    # Convert to MAC fraction
    mac_divisor = MAC if MAC != 0 else 1

    pa_mac = [((c - X_LEMAC) / mac_divisor) for c in pa_CG]
    pb_mac = [((c - X_LEMAC) / mac_divisor) for c in pb_CG]
    f_mac = [((c - X_LEMAC) / mac_divisor) for c in f_CG]

    # --- 3. CALCULATE CG EXTREMES & LIMITS ---
    all_cg_mac = pa_mac + pb_mac + f_mac

    most_fwd_cg = min(all_cg_mac)
    most_aft_cg = max(all_cg_mac)

    # Apply the margin to widen the envelope
    fwd_limit_with_margin = most_fwd_cg - CG_MARGIN
    aft_limit_with_margin = most_aft_cg + CG_MARGIN

    # --- 4. PRINTING & PLOTTING (Toggled by 'plot' boolean) ---
    if plot:
        print(f"--- CG LIMITS SUMMARY (Professional Style) ---")
        print(f"Most Forward CG (Calculated): {most_fwd_cg:.4f} MAC")
        print(f"Most Aft CG (Calculated):     {most_aft_cg:.4f} MAC")
        print(f"Margin Applied:               ±{CG_MARGIN:.4f} MAC")
        print(f"FWD Limit with Margin:        {fwd_limit_with_margin:.4f} MAC")
        print(f"AFT Limit with Margin:        {aft_limit_with_margin:.4f} MAC")
        print(f"-------------------------\n")

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

        # Index helpers
        n_c = 3
        n_w = n_c + NUM_ROWS
        n_a = n_w + NUM_ROWS

        # ── Path A (solid — front-to-back) ──
        ax.plot(pa_mac[:n_c], pa_W[:n_c],
                color=COL_CARGO, marker='s', ms=5, lw=1.8,
                label='Cargo (fwd → aft)', zorder=3)
        ax.plot(pa_mac[n_c-1:n_w], pa_W[n_c-1:n_w],
                color=COL_WIN, marker='o', ms=3.5, lw=1.4,
                label='Window pax (fwd → aft)', zorder=3)
        ax.plot(pa_mac[n_w-1:n_a], pa_W[n_w-1:n_a],
                color=COL_AISLE, marker='o', ms=3.5, lw=1.4,
                label='Aisle pax (fwd → aft)', zorder=3)

        # ── Path B (dashed — back-to-front) ──
        ax.plot(pb_mac[:n_c], pb_W[:n_c],
                color=COL_CARGO, marker='s', ms=5, lw=1.8, ls='--', zorder=3)
        ax.plot(pb_mac[n_c-1:n_w], pb_W[n_c-1:n_w],
                color=COL_WIN, marker='o', ms=3.5, lw=1.4, ls='--', zorder=3)
        ax.plot(pb_mac[n_w-1:n_a], pb_W[n_w-1:n_a],
                color=COL_AISLE, marker='o', ms=3.5, lw=1.4, ls='--', zorder=3)

        # ── Fuel loading ──
        ax.plot(f_mac, f_W, color=COL_FUEL, lw=3, solid_capstyle='round',
                label='Fuel loading', zorder=4)

        # ── OEW marker & label ──
        ax.scatter([pa_mac[0]], [OEW], color='black', s=100, zorder=6,
                   edgecolors='white', linewidths=1.2)
        ax.text(pa_mac[0] + 0.012, OEW - 600, f'OEW = {OEW:,.0f} kg',
                color='black', fontsize=9, fontweight='bold', zorder=7,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))
                
        ax.axvline(x=fwd_limit_with_margin, color=COL_LIMIT, ls='-', lw=1.5, alpha=0.7,
                   label=f'CG limits ± {CG_MARGIN:.0%} MAC')
        ax.axvline(x=aft_limit_with_margin, color=COL_LIMIT, ls='-', lw=1.5, alpha=0.7)

        # Calculated CG extremes (thin dashed)
        ax.axvline(x=most_fwd_cg, color='grey', ls='--', lw=0.8, alpha=0.5)
        ax.axvline(x=most_aft_cg, color='grey', ls='--', lw=0.8, alpha=0.5)

        # ── MZFW line ──
        MZFW_CALC = pa_W[-1]  # Weight before fuel is added
        ax.axhline(y=MZFW_CALC, color='#555555', ls='--', lw=1.5, alpha=0.6)
        
        # We need the current xlim to place text, so we force an update
        plt.draw()
        x_min = ax.get_xlim()[0]
        ax.text(x_min + 0.01 if x_min != 0 else most_fwd_cg,
                MZFW_CALC + 250, f'MZFW = {MZFW_CALC:,.0f} kg',
                color='#444444', fontsize=9, fontweight='bold')

        # ── MTOW line ──
        ax.axhline(y=MTOW, color=COL_LIMIT, ls='--', lw=1.5, alpha=0.6)
        ax.text(x_min + 0.01 if x_min != 0 else most_fwd_cg,
                MTOW + 250, f'MTOW = {MTOW:,.0f} kg',
                color=COL_LIMIT, fontsize=9, fontweight='bold')

        # ── Axes ──
        try:
            ax.set_xlim(fwd_limit_with_margin - 0.06, aft_limit_with_margin + 0.08)
        except ValueError:
            pass
        ax.set_ylim(OEW - 1200, MTOW + 2500)

        ax.set_title('CRJ-1000 — Loading Envelope (Potato Diagram)',
                      fontweight='bold', pad=14)
        ax.set_xlabel(r'$x_{\mathrm{cg}}\;/\;\mathrm{MAC}$')
        ax.set_ylabel('Aircraft Mass  (kg)')

        # ── Legend ──
        leg = ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), 
                        frameon=True, fancybox=False,
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

        # Use an explicit tight_layout with a rect to ensure the external legend fits
        plt.tight_layout(rect=[0, 0, 0.85, 1])
        plt.show()

    # Return the core calculated limits
    return most_fwd_cg, most_aft_cg, fwd_limit_with_margin, aft_limit_with_margin


# --- 5. EXECUTION ---
if __name__ == '__main__':
    # Pull all data from the nose reference point
    cg_data_from_nose = cg.calculate_aircraft_cgs(ip.x_LEMACw)["from_nose"]

    # Extract the required values using the correct dictionary paths
    X_OEW_CURRENT = cg_data_from_nose["aircraft"]
    X_WING_CURRENT = cg_data_from_nose["components"]["wing"]
    X_LEMAC_CURRENT = ip.x_LEMACw

    # Run the function, plotting and printing enabled
    fwd, aft, fwd_margin, aft_margin = calculate_cg_limits(
        X_OEW=X_OEW_CURRENT,
        X_LEMAC=X_LEMAC_CURRENT,
        X_FUEL=X_WING_CURRENT,
        plot=True
    )