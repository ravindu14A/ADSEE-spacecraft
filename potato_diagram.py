import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

# Import EXX inputs and CG calculation module
import Input_updated as ip
import CG_positions_updated as cg


# =====================================================================
# HELPER
# =====================================================================
def add_mass(current_w, current_cg, added_w, added_cg):
    """Calculate resulting weight and CG after adding a mass item."""
    new_w = current_w + added_w
    if new_w == 0:
        return 0, current_cg
    new_cg = (current_w * current_cg + added_w * added_cg) / new_w
    return new_w, new_cg


# =====================================================================
# MAIN FUNCTION
# =====================================================================
def calculate_cg_limits(plot=True):
    """
    Generates the CRJ-EXX Potato Diagram.

    Loading order (per assignment):
        1. OEW + Batteries  (starting point)
        2. Cargo             (two ordering paths A/B)
        3. Window-seat pax   (front→back A, back→front B)
        4. Aisle-seat pax    (front→back A, back→front B)
        5. Fuel              (up to MTOW)

    Returns
    -------
    most_fwd_cg, most_aft_cg, fwd_limit, aft_limit  (all in MAC fraction)
    """

    # ------------------------------------------------------------------
    # 1. GATHER DATA
    # ------------------------------------------------------------------
    MAC = cg.c_macw
    X_LEMAC = ip.x_LEMACw

    # Compute EOW+Battery CG automatically
    cg_results = cg.calculate_aircraft_cgs(X_LEMAC)
    X_EOW = cg_results["from_nose"]["aircraft"]

    # --- Correct EOW computation ---
    # Input_updated.py weight fractions are stored as percentages but
    # multiplied by ip.EOW without dividing by 100.  We recompute here
    # using the base EOW from Input.py (23 188 kg).
    import Input as ip_base
    BASE_EOW = ip_base.EOW                              # 23 188 kg

    W_wing   = 19.7 / 100 * BASE_EOW * 0.91
    W_htail  =  2.5 / 100 * BASE_EOW
    W_vtail  =  1.8 / 100 * BASE_EOW
    W_fus    = 35.0 / 100 * BASE_EOW * 0.93
    W_mlg    =  5.8 / 100 * BASE_EOW
    W_nlg    =  0.8 / 100 * BASE_EOW
    W_prop   = 13.3 / 100 * BASE_EOW
    W_cockp  =  2.3 / 100 * BASE_EOW

    BATT_MASS = ip.MASS_BATT_FRONT + ip.MASS_BATT_AFT   # 4 500 kg
    EOW_STRUCT = (W_wing + W_htail + W_vtail + W_fus
                  + W_mlg + W_nlg + W_prop + W_cockp
                  + ip.WEIGHT_BATTERY_FWD + ip.WEIGHT_BATTERY_AFT
                  + BATT_MASS)
    START_WEIGHT = EOW_STRUCT + BATT_MASS                # EOW + batteries

    MTOW = ip.MTOW
    TOTAL_PAX_WT = ip.NUM_ROWS * 4 * ip.MASS_PAX
    TOTAL_CARGO  = ip.MASS_FRONT_CARGO_EXX + ip.MASS_AFT_CARGO_EXX
    MZFW = START_WEIGHT + TOTAL_PAX_WT + TOTAL_CARGO
    MAX_FUEL = MTOW - MZFW
    X_FUEL = ip.X_FUEL

    # Cargo (redistributed for EXX)
    MASS_FRONT_CARGO = ip.MASS_FRONT_CARGO_EXX
    MASS_AFT_CARGO = ip.MASS_AFT_CARGO_EXX
    X_FRONT_CARGO = ip.X_FRONT_CARGO
    X_AFT_CARGO = ip.X_AFT_CARGO

    # Passengers
    MASS_PAX = ip.MASS_PAX
    NUM_ROWS = ip.NUM_ROWS
    row_positions = [ip.X_ROW_1 + i * ip.ROW_PITCH for i in range(NUM_ROWS)]

    CG_MARGIN = 0.05  # ±5 % MAC safety margin

    # ------------------------------------------------------------------
    # 2. BUILD LOADING PATHS
    # ------------------------------------------------------------------
    # Path A: forward-first loading   |   Path B: aft-first loading
    pa_W = [START_WEIGHT];  pa_CG = [X_EOW]
    pb_W = [START_WEIGHT];  pb_CG = [X_EOW]

    # ---- Cargo ----
    # Path A: front cargo → aft cargo
    w, c = add_mass(pa_W[-1], pa_CG[-1], MASS_FRONT_CARGO, X_FRONT_CARGO)
    pa_W.append(w); pa_CG.append(c)
    w, c = add_mass(pa_W[-1], pa_CG[-1], MASS_AFT_CARGO, X_AFT_CARGO)
    pa_W.append(w); pa_CG.append(c)

    # Path B: aft cargo → front cargo
    w, c = add_mass(pb_W[-1], pb_CG[-1], MASS_AFT_CARGO, X_AFT_CARGO)
    pb_W.append(w); pb_CG.append(c)
    w, c = add_mass(pb_W[-1], pb_CG[-1], MASS_FRONT_CARGO, X_FRONT_CARGO)
    pb_W.append(w); pb_CG.append(c)

    # ---- Window Seats (2 pax per row) ----
    for x in row_positions:
        w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
        pa_W.append(w); pa_CG.append(c)
    for x in reversed(row_positions):
        w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
        pb_W.append(w); pb_CG.append(c)

    # ---- Aisle Seats (2 pax per row) ----
    for x in row_positions:
        w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
        pa_W.append(w); pa_CG.append(c)
    for x in reversed(row_positions):
        w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
        pb_W.append(w); pb_CG.append(c)

    # Index helpers for plotting segments
    n_cargo = 3                               # indices 0-2
    n_window = n_cargo + NUM_ROWS             # indices 2 .. 2+NUM_ROWS
    n_aisle = n_window + NUM_ROWS             # rest

    # ---- Fuel Loading ----
    f_W = [pa_W[-1]];  f_CG = [pa_CG[-1]]
    for f in np.linspace(0, MAX_FUEL, 40)[1:]:
        fuel_to_add = min(f, MTOW - f_W[0])
        if fuel_to_add <= 0:
            break
        w, c = add_mass(f_W[0], f_CG[0], fuel_to_add, X_FUEL)
        f_W.append(w); f_CG.append(c)

    # ------------------------------------------------------------------
    # 3. CONVERT TO MAC FRACTION
    # ------------------------------------------------------------------
    mac_div = MAC if MAC != 0 else 1.0
    pa_mac = [(c - X_LEMAC) / mac_div for c in pa_CG]
    pb_mac = [(c - X_LEMAC) / mac_div for c in pb_CG]
    f_mac  = [(c - X_LEMAC) / mac_div for c in f_CG]

    # ------------------------------------------------------------------
    # 4. CG LIMITS
    # ------------------------------------------------------------------
    all_cg = pa_mac + pb_mac + f_mac
    most_fwd_cg = min(all_cg)
    most_aft_cg = max(all_cg)
    fwd_limit = most_fwd_cg - CG_MARGIN
    aft_limit = most_aft_cg + CG_MARGIN

    # ------------------------------------------------------------------
    # 5. PRINT SUMMARY
    # ------------------------------------------------------------------
    if plot:
        print("=" * 50)
        print("  CRJ-EXX  POTATO DIAGRAM — CG LIMITS")
        print("=" * 50)
        print(f"  EOW+Batt weight : {START_WEIGHT:.1f} kg")
        print(f"  EOW+Batt CG     : {X_EOW:.3f} m from nose")
        print(f"  MTOW            : {MTOW:.1f} kg")
        print(f"  MZFW            : {MZFW:.1f} kg")
        print(f"  Max fuel        : {MAX_FUEL:.1f} kg")
        print("-" * 50)
        print(f"  Most FWD CG     : {most_fwd_cg:.4f} MAC")
        print(f"  Most AFT CG     : {most_aft_cg:.4f} MAC")
        print(f"  Margin          : ±{CG_MARGIN:.2f} MAC")
        print(f"  FWD limit       : {fwd_limit:.4f} MAC")
        print(f"  AFT limit       : {aft_limit:.4f} MAC")
        print("=" * 50)

    # ------------------------------------------------------------------
    # 6. PLOT
    # ------------------------------------------------------------------
    if plot:
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        # Colour palette
        c_cargo = '#9D4EDD'
        c_win   = '#4895EF'
        c_ais   = '#F72585'
        c_fuel  = '#4CC9F0'

        # --- Path A (solid) ---
        ax.plot(pa_mac[:n_cargo], pa_W[:n_cargo],
                color=c_cargo, marker='o', markersize=4, label='Cargo')
        ax.plot(pa_mac[n_cargo-1:n_window], pa_W[n_cargo-1:n_window],
                color=c_win, marker='o', markersize=3, label='Window Pax')
        ax.plot(pa_mac[n_window-1:n_aisle], pa_W[n_window-1:n_aisle],
                color=c_ais, marker='o', markersize=3, label='Aisle Pax')

        # --- Path B (dashed) ---
        ax.plot(pb_mac[:n_cargo], pb_W[:n_cargo],
                color=c_cargo, marker='o', markersize=4, linestyle='--')
        ax.plot(pb_mac[n_cargo-1:n_window], pb_W[n_cargo-1:n_window],
                color=c_win, marker='o', markersize=3, linestyle='--')
        ax.plot(pb_mac[n_window-1:n_aisle], pb_W[n_window-1:n_aisle],
                color=c_ais, marker='o', markersize=3, linestyle='--')

        # --- Fuel ---
        ax.plot(f_mac, f_W, color=c_fuel, linewidth=4, label='Fuel Loading')

        # --- Reference markers ---
        ax.scatter([pa_mac[0]], [START_WEIGHT], color='white', s=120, zorder=5,
                   label=f'EOW+Batt ({START_WEIGHT:.0f} kg)')

        # CG limit lines
        ax.axvline(x=most_fwd_cg, color='yellow', ls=':', alpha=0.6,
                   label=f'Most FWD ({most_fwd_cg:.3f})')
        ax.axvline(x=most_aft_cg, color='orange', ls=':', alpha=0.6,
                   label=f'Most AFT ({most_aft_cg:.3f})')
        ax.axvline(x=fwd_limit, color='red', ls='-', alpha=0.8,
                   label='FWD limit w/ margin')
        ax.axvline(x=aft_limit, color='red', ls='-', alpha=0.8,
                   label='AFT limit w/ margin')

        # Weight limit lines
        ax.axhline(y=MTOW, color='red', ls='--', alpha=0.5)
        ax.text(ax.get_xlim()[1], MTOW, '  MTOW', color='red',
                va='center', fontweight='bold')
        ax.axhline(y=MZFW, color='cyan', ls='--', alpha=0.4)
        ax.text(ax.get_xlim()[1], MZFW, '  MZFW', color='cyan',
                va='center', fontweight='bold')

        # Axes
        try:
            ax.set_xlim(fwd_limit - 0.05, aft_limit + 0.10)
        except ValueError:
            pass
        ax.set_ylim(START_WEIGHT - 1000, MTOW + 2000)

        ax.set_title("CRJ-EXX Potato Diagram (Loading Envelope)",
                      fontsize=16, color='white', fontweight='bold', pad=20)
        ax.set_xlabel("$x_{cg}\\;/\\;\\mathrm{MAC}$", fontsize=13)
        ax.set_ylabel("Mass  (kg)", fontsize=13)
        ax.legend(loc='upper left', frameon=True, facecolor='#222', fontsize=9)
        ax.grid(True, alpha=0.15)

        plt.tight_layout()
        plt.show()

    return most_fwd_cg, most_aft_cg, fwd_limit, aft_limit


# =====================================================================
# EXECUTION
# =====================================================================
if __name__ == '__main__':
    fwd, aft, fwd_m, aft_m = calculate_cg_limits(plot=True)
