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

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        c_cargo, c_win, c_ais, c_fuel = '#9D4EDD', '#4895EF', '#F72585', '#4CC9F0'

        n_cargo = 3
        n_win = n_cargo + NUM_ROWS
        n_aisle = n_win + NUM_ROWS

        # Plot Path A
        ax.plot(pa_mac[:n_cargo], pa_W[:n_cargo], color=c_cargo, marker='o', markersize=4, label='Cargo')
        ax.plot(pa_mac[n_cargo - 1:n_win], pa_W[n_cargo - 1:n_win], color=c_win, marker='o', markersize=3,
                label='Window Pax')
        ax.plot(pa_mac[n_win - 1:n_aisle], pa_W[n_win - 1:n_aisle], color=c_ais, marker='o', markersize=3,
                label='Aisle Pax')

        # Plot Path B
        ax.plot(pb_mac[:n_cargo], pb_W[:n_cargo], color=c_cargo, marker='o', markersize=4, linestyle='--')
        ax.plot(pb_mac[n_cargo - 1:n_win], pb_W[n_cargo - 1:n_win], color=c_win, marker='o', markersize=3,
                linestyle='--')
        ax.plot(pb_mac[n_win - 1:n_aisle], pb_W[n_win - 1:n_aisle], color=c_ais, marker='o', markersize=3,
                linestyle='--')

        ax.plot(f_mac, f_W, color=c_fuel, linewidth=4, label='Fuel Loading')
        ax.scatter([pa_mac[0]], [OEW], color='white', s=100, zorder=5, label='OEW CG')

        ax.axvline(x=most_fwd_cg, color='yellow', linestyle=':', alpha=0.6)
        ax.axvline(x=most_aft_cg, color='orange', linestyle=':', alpha=0.6)
        ax.axvline(x=fwd_limit_with_margin, color='red', linestyle='-', alpha=0.8, label='Limits w/ Margin')
        ax.axvline(x=aft_limit_with_margin, color='red', linestyle='-', alpha=0.8)

        ax.set_ylim(OEW - 1000, MTOW + 2000)
        ax.set_title("Aircraft Static Potato Diagram", fontsize=16, color='white', fontweight='bold', pad=20)
        ax.set_xlabel("$x_{cg} / MAC$", fontsize=12)
        ax.set_ylabel("Mass (kg)", fontsize=12)
        ax.legend(loc='upper left', frameon=True, facecolor='#222', fontsize=9)
        ax.grid(True, alpha=0.15)
        ax.axhline(y=MTOW, color='red', linestyle='--', alpha=0.5)

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