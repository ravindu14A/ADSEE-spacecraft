import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import Input_updated as ip
import CG_positions_updated as cg

def add_mass(current_w, current_cg, added_w, added_cg):
    """Helper function to calculate new weight and CG."""
    new_w = current_w + added_w

    # Safeguard against division by zero
    if new_w == 0:
        return 0, current_cg

    new_cg = ((current_w * current_cg) + (added_w * added_cg)) / new_w
    return new_w, new_cg

def calculate_cg_limits(X_OEW, X_LEMAC, plot=False):
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
    MAX_FUEL = ip.MAX_FUEL
    X_FUEL = ip.X_FUEL

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
        print(f"--- CG LIMITS SUMMARY ---")
        print(f"Most Forward CG (Calculated): {most_fwd_cg:.4f} MAC")
        print(f"Most Aft CG (Calculated):     {most_aft_cg:.4f} MAC")
        print(f"Margin Applied:               ±{CG_MARGIN:.4f} MAC")
        print(f"FWD Limit with Margin:        {fwd_limit_with_margin:.4f} MAC")
        print(f"AFT Limit with Margin:        {aft_limit_with_margin:.4f} MAC")
        print(f"-------------------------\n")

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        # Neon Color Palette
        c_cargo, c_win, c_ais, c_fuel = '#9D4EDD', '#4895EF', '#F72585', '#4CC9F0'

        # Plot Path A (Front-to-Back Loading)
        ax.plot(pa_mac[:3], pa_W[:3], color=c_cargo, marker='o', markersize=4, label='Cargo')
        ax.plot(pa_mac[2:28], pa_W[2:28], color=c_win, marker='o', markersize=3, label='Window Pax')
        ax.plot(pa_mac[27:], pa_W[27:], color=c_ais, marker='o', markersize=3, label='Aisle Pax')

        # Plot Path B (Back-to-Front Loading)
        ax.plot(pb_mac[:3], pb_W[:3], color=c_cargo, marker='o', markersize=4, linestyle='--')
        ax.plot(pb_mac[2:28], pb_W[2:28], color=c_win, marker='o', markersize=3, linestyle='--')
        ax.plot(pb_mac[27:], pb_W[27:], color=c_ais, marker='o', markersize=3, linestyle='--')

        # Plot Fuel Loading
        ax.plot(f_mac, f_W, color=c_fuel, linewidth=4, label='Fuel Loading')

        # Mark the OEW Point
        ax.scatter([pa_mac[0]], [OEW], color='white', s=100, zorder=5, label='OEW CG')

        # Plot the calculated limits & margins
        ax.axvline(x=most_fwd_cg, color='yellow', linestyle=':', alpha=0.6, label=f'Most FWD ({most_fwd_cg:.3f})')
        ax.axvline(x=most_aft_cg, color='orange', linestyle=':', alpha=0.6, label=f'Most AFT ({most_aft_cg:.3f})')

        ax.axvline(x=fwd_limit_with_margin, color='red', linestyle='-', alpha=0.8, label='FWD Limit w/ Margin')
        ax.axvline(x=aft_limit_with_margin, color='red', linestyle='-', alpha=0.8, label='AFT Limit w/ Margin')

        # Format axes limits
        try:
            ax.set_xlim(fwd_limit_with_margin - 0.05, aft_limit_with_margin + 0.1)
        except ValueError:
            pass
        ax.set_ylim(OEW - 1000, MTOW + 2000)

        # Labels & Grids
        ax.set_title("Aircraft Static Potato Diagram", fontsize=16, color='white', fontweight='bold', pad=20)
        ax.set_xlabel("$x_{cg} / MAC$", fontsize=12)
        ax.set_ylabel("Mass (kg)", fontsize=12)
        ax.legend(loc='upper left', frameon=True, facecolor='#222', fontsize=9)
        ax.grid(True, alpha=0.15)

        # Horizontal limit lines
        ax.axhline(y=MTOW, color='red', linestyle='--', alpha=0.5)
        ax.text(ax.get_xlim()[1], MTOW, ' MTOW', color='red', va='center', fontweight='bold')

        plt.tight_layout()
        plt.show()

    # Return the core calculated limits
    return most_fwd_cg, most_aft_cg, fwd_limit_with_margin, aft_limit_with_margin


# --- 5. EXECUTION ---
if __name__ == '__main__':
    # Dynamically pull the current EOW CG and LEMAC from your scripts
    X_OEW_CURRENT =  cg.calculate_aircraft_cgs(ip.x_LEMACw)["from_nose"]["aircraft"]   # Assuming this is your calculated total EOW CG from nose
    X_LEMAC_CURRENT = ip.x_LEMACw

    # Run the function, plotting and printing enabled
    fwd, aft, fwd_margin, aft_margin = calculate_cg_limits(
        X_OEW=X_OEW_CURRENT,
        X_LEMAC=X_LEMAC_CURRENT,
        plot=True
    )