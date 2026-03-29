import numpy as np
import matplotlib.pyplot as plt

# Import your core modules
import Input_updated as ip
import CG_positions_updated as cg
import potato_bandi_updated as pb

# Import the X-plot data (Ensure your X-plot file is saved as X_plot_updated.py)
# Because the variables in X_plot are calculated globally, we can access them directly!
import X_plot_updated as xp


def generate_combined_plot(min_lemacw=17.0, max_lemacw=19.0, num_points=50):
    print("Calculating CG Margins...")

    # 1. Calculate CG Margins Sweep (Replicating the loop to grab the arrays)
    x_lemac_array = np.linspace(min_lemacw, max_lemacw, num_points)
    fwd_cg_limits = []
    aft_cg_limits = []
    y_axis_ratios = []

    for x_lemac in x_lemac_array:
        cg_results = cg.calculate_aircraft_cgs(x_lemac)
        current_x_oew = cg_results["from_nose"]["aircraft"]
        _, _, fwd_margin, aft_margin = pb.calculate_cg_limits(current_x_oew, x_lemac, plot=False)

        fwd_cg_limits.append(fwd_margin)
        aft_cg_limits.append(aft_margin)
        y_axis_ratios.append(x_lemac / ip.l_fus)

    # 2. Get the specific limits for the CURRENT x_LEMACw to draw the red line
    curr_cg_results = cg.calculate_aircraft_cgs(ip.x_LEMACw)
    curr_x_oew = curr_cg_results["from_nose"]["aircraft"]
    _, _, curr_fwd_margin, curr_aft_margin = pb.calculate_cg_limits(curr_x_oew, ip.x_LEMACw, plot=False)
    curr_lemac_ratio = ip.x_LEMACw / ip.l_fus

    print("Generating Combined Overlay Plot...")

    # 3. Setup the Figure and Axes
    plt.style.use('default')
    fig, ax1 = plt.subplots(figsize=(12, 8))

    # --- AXIS 1: CG MARGINS (Left Y-Axis) ---
    color_cg = '#005f73'
    ax1.set_xlabel('CG Position ($x_{cg} / MAC$)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Normalized Wing Position ($X_{LEMACw} / l_{fus}$)', color=color_cg, fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color_cg)

    # Plot Envelope
    l1, = ax1.plot(fwd_cg_limits, y_axis_ratios, color='blue', linewidth=2, label='FWD CG Limit (w/ Margin)')
    l2, = ax1.plot(aft_cg_limits, y_axis_ratios, color='red', linewidth=2, linestyle='-',
                   label='AFT CG Limit (w/ Margin)')
    ax1.fill_betweenx(y_axis_ratios, fwd_cg_limits, aft_cg_limits, color='gray', alpha=0.1)

    # Draw the Red Connecting Line for Current LEMAC
    l3, = ax1.plot([curr_fwd_margin, curr_aft_margin], [curr_lemac_ratio, curr_lemac_ratio],
                   color='red', linewidth=3, marker='|', markersize=12,
                   label=f'Current Config (LEMAC={ip.x_LEMACw}m)')

    # --- AXIS 2: SCISSOR PLOT (Right Y-Axis) ---
    ax2 = ax1.twinx()
    color_scis = '#277da1'
    ax2.set_ylabel('Horizontal Tail Area Ratio ($S_h / S$)', color=color_scis, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color_scis)

    # Ensure limits match your original X_plot limits
    ax2.set_ylim(0.0, 0.4)

    # Plot Aerodynamic Boundaries
    l4, = ax2.plot(xp.x_np, xp.Sh_S_array, color='black', linestyle=':', linewidth=2, label='Neutral Point')
    l5, = ax2.plot(xp.x_aft_limit, xp.Sh_S_array, color='purple', linewidth=2, label='Aft Limit (Stability)')
    l6, = ax2.plot(xp.x_fwd_limit, xp.Sh_S_array, color='green', linewidth=2, label='Forward Limit (Control)')

    # --- 4. FORMATTING & LEGEND ---
    ax1.set_title("Combined Scissor Plot & CG Margins Envelope", fontsize=16, fontweight='bold', pad=20)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Combine legends from both axes and place them at the bottom
    lines = [l1, l2, l3, l4, l5, l6]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=True)

    plt.tight_layout()
    plt.show()


# =====================================================================
# EXECUTION
# =====================================================================
if __name__ == '__main__':
    # Adjust sweep limits based on your aircraft
    generate_combined_plot(min_lemacw=17.0, max_lemacw=21.0, num_points=60)