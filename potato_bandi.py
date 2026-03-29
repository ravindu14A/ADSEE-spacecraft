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

        # Set default safe style and force white background
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        # Standard Professional Color Palette
        c_cargo, c_win, c_ais, c_fuel = 'dimgrey', 'royalblue', 'seagreen', 'mediumturquoise'
        # Marker settings: solid red circles for key envelope points
        marker_pax = dict(marker='o', markersize=5, markerfacecolor='red', markeredgecolor='none')

        # Plot Path A (Front-to-Back Loading)
        ax.plot(pa_mac[:3], pa_W[:3], color=c_cargo, marker='o', markersize=4, label='Cargo (A)')
        ax.plot(pa_mac[2:28], pa_W[2:28], color=c_win, label='Window Pax (A)', **marker_pax)
        ax.plot(pa_mac[27:], pa_W[27:], color=c_ais, label='Aisle Pax (A)', **marker_pax)

        # Plot Path B (Back-to-Front Loading)
        ax.plot(pb_mac[:3], pb_W[:3], color=c_cargo, marker='o', markersize=4, linestyle='--')
        ax.plot(pb_mac[2:28], pb_W[2:28], color=c_win, linestyle='--', **marker_pax)
        ax.plot(pb_mac[27:], pb_W[27:], color=c_ais, linestyle='--', **marker_pax)

        # Plot Fuel Loading
        ax.plot(f_mac, f_W, color=c_fuel, linewidth=3, label='Fuel Loading')

        # Mark the OEW Point - Large prominent solid red circle
        ax.scatter([pa_mac[0]], [OEW], color='red', s=150, zorder=5, label='OEW CG Point')

        # Plot the calculated limits & margins - Using standard line styles
        ax.axvline(x=most_fwd_cg, color='dimgrey', linestyle='--', alpha=0.6, label=f'Most FWD ({most_fwd_cg:.3f})')
        ax.axvline(x=most_aft_cg, color='dimgrey', linestyle='--', alpha=0.6, label=f'Most AFT ({most_aft_cg:.3f})')

        ax.axvline(x=fwd_limit_with_margin, color='red', linestyle='-', alpha=0.8, label='FWD Limit w/ Margin')
        ax.axvline(x=aft_limit_with_margin, color='red', linestyle='-', alpha=0.8, label='AFT Limit w/ Margin')

        # Format axes limits
        try:
            ax.set_xlim(fwd_limit_with_margin - 0.05, aft_limit_with_margin + 0.1)
        except ValueError:
            pass
        ax.set_ylim(OEW - 1000, MTOW + 2000)

        # Labels & Grids
        ax.set_title("Aircraft Static Potato Diagram", fontsize=16, color='black', fontweight='bold', pad=20)
        ax.set_xlabel("$x_{cg} / MAC$", fontsize=12)
        ax.set_ylabel("Mass (kg)", fontsize=12)

        # Professional legend with black text
        ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=1, edgecolor='dimgrey', fontsize=9,
                  labelcolor='black')
        ax.grid(True, linestyle='-', color='lightgrey', alpha=0.7)

        # Horizontal limit lines - Bold professional style
        ax.axhline(y=MTOW, color='red', linestyle='--', linewidth=2, alpha=0.5)
        ax.text(ax.get_xlim()[1], MTOW, ' MTOW', color='red', va='center', fontweight='bold')

        plt.tight_layout()
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