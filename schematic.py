import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

# Import your variables from the separate Input file
import Input as ip


# ------------------------------------
# GEOMETRY CALCULATOR FUNCTIONS
# ------------------------------------
def get_lifting_surface_coords(x_lemac, b, c_r, taper, sweep_deg):
    """Calculates trapezoid coordinates for wings and tails using MAC position."""
    sweep_rad = np.radians(sweep_deg)

    # Calculate MAC spanwise position (y_mac)
    y_mac = (b / 6) * ((1 + 2 * taper) / (1 + taper))

    # Distance from root LE to MAC LE
    dx_mac = y_mac * np.tan(sweep_rad)

    # Root leading edge position
    x_root_le = x_lemac - dx_mac
    c_t = c_r * taper  # Tip chord

    # Right side coordinates: [Root LE, Root TE, Tip TE, Tip LE]
    x_tip_le = x_root_le + (b / 2) * np.tan(sweep_rad)

    right_surface = np.array([
        [x_root_le, 0],
        [x_root_le + c_r, 0],
        [x_tip_le + c_t, b / 2],
        [x_tip_le, b / 2]
    ])

    # Left side coordinates (mirror y-axis)
    left_surface = right_surface.copy()
    left_surface[:, 1] = -left_surface[:, 1]

    return right_surface, left_surface


# ------------------------------------
# PLOTTING EXECUTION
# ------------------------------------
if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(12, 8))

    # 1. Draw Fuselage (Rectangle centered at y=0, starting at x=0)
    # Origin is bottom-left corner of the rectangle for matplotlib
    fuselage = Rectangle((0, -ip.d_fus / 2), ip.l_fus, ip.d_fus,
                         edgecolor='black', facecolor='lightgray', zorder=2, label='Fuselage')
    ax.add_patch(fuselage)

    # 2. Draw Main Wings
    right_wing, left_wing = get_lifting_surface_coords(ip.x_LEMACw, ip.b_w, ip.c_rw, ip.TAPER_RATIOw, ip.SWEEP_ANGLEw)
    ax.add_patch(Polygon(right_wing, edgecolor='blue', facecolor='lightblue', alpha=0.7, zorder=1, label='Main Wing'))
    ax.add_patch(Polygon(left_wing, edgecolor='blue', facecolor='lightblue', alpha=0.7, zorder=1))

    # 3. Draw Horizontal Stabilizer
    right_htail, left_htail = get_lifting_surface_coords(ip.x_LEMACh, ip.b_h, ip.c_rh, ip.TAPER_RATIOh, ip.SWEEP_ANGLEh)
    ax.add_patch(Polygon(right_htail, edgecolor='green', facecolor='lightgreen', alpha=0.7, zorder=1, label='H-Stab'))
    ax.add_patch(Polygon(left_htail, edgecolor='green', facecolor='lightgreen', alpha=0.7, zorder=1))

    # 4. Draw Nacelles (Assuming rear-fuselage mount since x=30 is far aft)
    if ip.y_centrenacelle is None:
        # Place them flush against the fuselage sides
        y_nac_right = ip.d_fus / 2
        y_nac_left = -ip.d_fus / 2 - ip.d_nac
    else:
        y_nac_right = ip.y_centrenacelle - ip.d_nac / 2
        y_nac_left = -ip.y_centrenacelle - ip.d_nac / 2

    nacelle_right = Rectangle((ip.x_startnacelle, y_nac_right), ip.l_nac, ip.d_nac,
                              edgecolor='red', facecolor='salmon', zorder=3, label='Nacelles')
    nacelle_left = Rectangle((ip.x_startnacelle, y_nac_left), ip.l_nac, ip.d_nac,
                             edgecolor='red', facecolor='salmon', zorder=3)
    ax.add_patch(nacelle_right)
    ax.add_patch(nacelle_left)

    # 5. Draw Landing Gear
    # Nose Wheel
    ax.scatter(ip.x_NW, 0, color='black', marker='o', s=50, zorder=4, label='Nose Gear')
    # Main Gear
    ax.scatter(ip.x_MG, ip.y_MG, color='black', marker='s', s=50, zorder=4, label='Main Gear')
    ax.scatter(ip.x_MG, -ip.y_MG, color='black', marker='s', s=50, zorder=4)

    # 6. Formatting the Plot
    ax.set_aspect('equal')  # CRITICAL: Ensures the plane isn't visually stretched/distorted
    ax.set_xlim(-2, ip.l_fus + 5)
    ax.set_ylim(-ip.b_w / 2 - 2, ip.b_w / 2 + 2)

    ax.set_title("Aircraft Top-Down 2D Schematic", fontsize=14, fontweight='bold')
    ax.set_xlabel("X Position from Nose (m)")
    ax.set_ylabel("Y Position from Centerline (m)")

    # Add a grid and a legend
    ax.grid(True, linestyle='--', alpha=0.6)

    # Filter out duplicate labels for the legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    plt.tight_layout()
    plt.show()