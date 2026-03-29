import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

# Import your updated variables and EXX CG calculator
import Input_updated as ip_up
import CG_positions_updated as cg_exx


# ------------------------------------
# GEOMETRY CALCULATOR FUNCTIONS
# ------------------------------------
def get_lifting_surface_coords(x_lemac, b, c_r, taper, sweep_deg):
    """Calculates trapezoid coordinates for wings and tails using MAC position."""
    sweep_rad = np.radians(sweep_deg)
    y_mac = (b / 6) * ((1 + 2 * taper) / (1 + taper))
    dx_mac = y_mac * np.tan(sweep_rad)

    x_root_le = x_lemac - dx_mac
    c_t = c_r * taper
    x_tip_le = x_root_le + (b / 2) * np.tan(sweep_rad)

    right_surface = np.array([
        [x_root_le, 0], [x_root_le + c_r, 0],
        [x_tip_le + c_t, b / 2], [x_tip_le, b / 2]
    ])
    left_surface = right_surface.copy()
    left_surface[:, 1] = -left_surface[:, 1]

    return right_surface, left_surface


def get_spar_lines(x_lemac, b, c_r, taper, sweep_deg, spar_fraction):
    """Calculates the x and y coordinate lists for drawing a spar line."""
    sweep_rad = np.radians(sweep_deg)
    y_mac = (b / 6) * ((1 + 2 * taper) / (1 + taper))
    x_root_le = x_lemac - (y_mac * np.tan(sweep_rad))
    c_t = c_r * taper
    x_tip_le = x_root_le + (b / 2) * np.tan(sweep_rad)

    root_spar_x = x_root_le + (spar_fraction * c_r)
    tip_spar_x = x_tip_le + (spar_fraction * c_t)

    right_spar = ([root_spar_x, tip_spar_x], [0, b / 2])
    left_spar = ([root_spar_x, tip_spar_x], [0, -b / 2])
    return right_spar, left_spar


# ------------------------------------
# PLOTTING EXECUTION
# ------------------------------------
if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(14, 9))

    # --- 1. CALCULATE CGS ---
    cg_data = cg_exx.calculate_aircraft_cgs(ip_up.x_LEMACw)
    cg_components = cg_data['from_nose']['components']

    # --- 2. DRAW SHAPES & SPARS ---
    # Fuselage
    fuselage = Rectangle((0, -ip_up.d_fus / 2), ip_up.l_fus, ip_up.d_fus,
                         edgecolor='black', facecolor='lightgray', zorder=2, label='Fuselage Outline')
    ax.add_patch(fuselage)

    # Main Wings
    right_wing, left_wing = get_lifting_surface_coords(ip_up.x_LEMACw, ip_up.b_w, ip_up.c_rw, ip_up.TAPER_RATIOw,
                                                       ip_up.SWEEP_ANGLEw)
    ax.add_patch(Polygon(right_wing, edgecolor='blue', facecolor='lightblue', alpha=0.5, zorder=1, label='Main Wing'))
    ax.add_patch(Polygon(left_wing, edgecolor='blue', facecolor='lightblue', alpha=0.5, zorder=1))

    # Wing Spars (Using fractions from input file)
    front_frac = getattr(ip_up, 'front_spar_fraction', 0.25)
    rear_frac = getattr(ip_up, 'rear_spar_fraction', 0.60)

    rf_spar, lf_spar = get_spar_lines(ip_up.x_LEMACw, ip_up.b_w, ip_up.c_rw, ip_up.TAPER_RATIOw, ip_up.SWEEP_ANGLEw,
                                      front_frac)
    rr_spar, lr_spar = get_spar_lines(ip_up.x_LEMACw, ip_up.b_w, ip_up.c_rw, ip_up.TAPER_RATIOw, ip_up.SWEEP_ANGLEw,
                                      rear_frac)

    ax.plot(rf_spar[0], rf_spar[1], color='black', linestyle='--', linewidth=1.5, zorder=2, label='Wing Spars')
    ax.plot(lf_spar[0], lf_spar[1], color='black', linestyle='--', linewidth=1.5, zorder=2)
    ax.plot(rr_spar[0], rr_spar[1], color='black', linestyle='--', linewidth=1.5, zorder=2)
    ax.plot(lr_spar[0], lr_spar[1], color='black', linestyle='--', linewidth=1.5, zorder=2)

    # Horizontal Stabilizer
    right_htail, left_htail = get_lifting_surface_coords(ip_up.x_LEMACh, ip_up.b_h, ip_up.c_rh, ip_up.TAPER_RATIOh,
                                                         ip_up.SWEEP_ANGLEh)
    ax.add_patch(Polygon(right_htail, edgecolor='green', facecolor='lightgreen', alpha=0.5, zorder=1, label='H-Stab'))
    ax.add_patch(Polygon(left_htail, edgecolor='green', facecolor='lightgreen', alpha=0.5, zorder=1))

    # Nacelles
    if ip_up.y_centrenacelle is None:
        y_nac_right = ip_up.d_fus / 2
        y_nac_left = -ip_up.d_fus / 2 - ip_up.d_nac
    else:
        y_nac_right = ip_up.y_centrenacelle - ip_up.d_nac / 2
        y_nac_left = -ip_up.y_centrenacelle - ip_up.d_nac / 2

    ax.add_patch(Rectangle((ip_up.x_startnacelle, y_nac_right), ip_up.l_nac, ip_up.d_nac,
                           edgecolor='red', facecolor='salmon', zorder=3, label='Nacelles (EXX)'))
    ax.add_patch(Rectangle((ip_up.x_startnacelle, y_nac_left), ip_up.l_nac, ip_up.d_nac,
                           edgecolor='red', facecolor='salmon', zorder=3))

    # --- 3. DRAW CG MARKERS & DOTS ---
    # Wheels
    ax.scatter(ip_up.x_NW, 0, color='black', marker='o', s=80, zorder=5, label='Nose Gear')
    ax.scatter(ip_up.x_MG, ip_up.y_MG, color='black', marker='s', s=80, zorder=5, label='Main Gear')
    ax.scatter(ip_up.x_MG, -ip_up.y_MG, color='black', marker='s', s=80, zorder=5)

    # Component CGs (Dynamic fetch)
    fus_cg = cg_components.get('Fuselage', cg_components.get('fuselage'))
    wing_cg = cg_components.get('Wing', cg_components.get('wing'))
    htail_cg = cg_components.get('Horizontal Tail', cg_components.get('horizontal_stab'))

    ax.scatter(fus_cg, 0, color='cyan', marker='X', edgecolor='black', s=120, zorder=6, label='Fuselage CG')
    ax.scatter(wing_cg, 0, color='blue', marker='X', edgecolor='white', s=120, zorder=6, label='Wing CG')
    ax.scatter(htail_cg, 0, color='green', marker='X', edgecolor='white', s=120, zorder=6, label='H-Stab CG')

    # Total Aircraft EXX Empty Weight CG
    ax.scatter(cg_data['from_nose']['aircraft'], 0, color='white', marker='*', edgecolor='black', s=300, zorder=7,
               label='Total EXX EOW CG')

    # Batteries (Front and Aft)
    ax.scatter(ip_up.X_BATT_FRONT, 0, color='yellow', marker='*', edgecolor='black', s=200, zorder=6,
               label='Front Battery CG')
    ax.scatter(ip_up.X_BATT_AFT, 0, color='yellow', marker='*', edgecolor='black', s=200, zorder=6,
               label='Aft Battery CG')

    # Cargo CGs
    ax.scatter([ip_up.X_FRONT_CARGO, ip_up.X_AFT_CARGO], [0, 0], color='orange', marker='D', edgecolor='black', s=80,
               zorder=6, label='Cargo CGs')

    # Passengers
    y_seat_offsets = [-1.05, -0.55, 0.55, 1.05]
    people_x, people_y = [], []
    for row in range(ip_up.NUM_ROWS):
        x = ip_up.X_ROW_1 + row * ip_up.ROW_PITCH
        if x > ip_up.l_fus: break
        for y_offset in y_seat_offsets:
            people_x.append(x)
            people_y.append(y_offset)
    ax.scatter(people_x, people_y, color='purple', marker='o', s=15, zorder=4, label='Passengers (EXX)')

    # --- 4. FORMATTING ---
    ax.set_aspect('equal')
    ax.set_xlim(-2, ip_up.l_fus + 5)
    ax.set_ylim(-ip_up.b_w / 2 - 2, ip_up.b_w / 2 + 2)

    ax.set_title("EXX Variant Top-Down 2D Schematic", fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel("X Position from Nose (m)", fontsize=12)
    ax.set_ylabel("Y Position from Centerline (m)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)

    plt.tight_layout()
    plt.show()