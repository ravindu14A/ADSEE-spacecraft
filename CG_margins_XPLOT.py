import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.widgets import Slider

# Import your modules from the same folder
import Input as ip
import CG_positions as cg
import potato_bandi as pb
import X_plot as xp


def generate_combined_plot(min_lemacw=10.0, max_lemacw=30.0, num_points=100):
    print(f"Sweeping X_LEMACw from {min_lemacw} to {max_lemacw}...")

    # 1. Calculate CG Margins Sweep
    x_lemac_array = np.linspace(min_lemacw, max_lemacw, num_points)
    fwd_cg_limits = []
    aft_cg_limits = []
    y_axis_ratios = []

    for x_lemac in x_lemac_array:
        # Get the updated OEW CG
        cg_results = cg.calculate_aircraft_cgs(x_lemac)
        current_x_oew = cg_results["from_nose"]["aircraft"]

        # STRICT EXTRACTION: Will throw KeyError if "wing" does not exist
        current_x_wing = cg_results["from_nose"]["components"]["wing"]

        # Get the CG envelope limits, passing X_FUEL
        _, _, fwd_margin, aft_margin = pb.calculate_cg_limits(
            X_OEW=current_x_oew,
            X_LEMAC=x_lemac,
            X_FUEL=current_x_wing,
            plot=False
        )

        fwd_cg_limits.append(fwd_margin)
        aft_cg_limits.append(aft_margin)
        y_axis_ratios.append(x_lemac / ip.l_fus)

    # 2. Get specific limits for the CURRENT x_LEMACw (For the Red Line)
    curr_cg_results = cg.calculate_aircraft_cgs(ip.x_LEMACw)
    curr_x_oew = curr_cg_results["from_nose"]["aircraft"]

    # STRICT EXTRACTION: Will throw KeyError if "wing" does not exist
    curr_x_wing = curr_cg_results["from_nose"]["components"]["wing"]

    # Pass X_FUEL for the current configuration calculation
    _, _, curr_fwd_margin, curr_aft_margin = pb.calculate_cg_limits(
        X_OEW=curr_x_oew,
        X_LEMAC=ip.x_LEMACw,
        X_FUEL=curr_x_wing,
        plot=False
    )
    curr_lemac_ratio = ip.x_LEMACw / ip.l_fus

    print("Sweep complete. Generating Combined Overlay Plot...")

    # 3. Setup the Figure and Axes
    plt.style.use('default')
    fig, ax1 = plt.subplots(figsize=(10, 8))  # Resized to fit sliders

    # Make room at the bottom for TWO sliders
    fig.subplots_adjust(bottom=0.30)

    # --- AXIS 1: CG MARGINS (Left Y-Axis) ---
    color_cg = '#1f77b4'  # Standard matplotlib blue
    ax1.set_xlabel('CG Position ($x_{cg}/MAC$)', fontsize=12)
    ax1.set_ylabel('Normalized Wing Position ($X_{LEMACw}/l_{fus}$)', color=color_cg, fontsize=12)
    ax1.tick_params(axis='y', labelcolor=color_cg)

    # Plot Envelope
    l1, = ax1.plot(fwd_cg_limits, y_axis_ratios, color='#003f5c', linewidth=1.5, label='FWD CG Limit (w/ Margin)')
    l2, = ax1.plot(aft_cg_limits, y_axis_ratios, color='#d45087', linewidth=1.5, linestyle='-',
                   label='AFT CG Limit (w/ Margin)')

    # Fill Envelope and create a proxy artist for the legend
    ax1.fill_betweenx(y_axis_ratios, fwd_cg_limits, aft_cg_limits, color='#eaeaea', alpha=0.7)
    fill_poly = Patch(facecolor='#eaeaea', edgecolor='none', alpha=0.7, label='Allowable CG Envelope')

    # Draw the Red Connecting Line for Current LEMAC
    l3, = ax1.plot([curr_fwd_margin, curr_aft_margin], [curr_lemac_ratio, curr_lemac_ratio],
                   color='#d45087', linewidth=2.0, marker='|', markeredgewidth=1.5, markersize=8,
                   label=f'Current Config (LEMAC={ip.x_LEMACw}m)')

    # Set initial base limits for the LEFT axis (Zoomed in on realistic values)
    base_y1_min = (ip.x_LEMACw - 3.0) / ip.l_fus
    base_y1_max = (ip.x_LEMACw + 3.0) / ip.l_fus
    ax1.set_ylim(base_y1_min, base_y1_max)

    # --- AXIS 2: SCISSOR PLOT (Right Y-Axis) ---
    ax2 = ax1.twinx()
    color_scis = '#2f4b7c'
    ax2.set_ylabel('Horizontal Tail Area Ratio ($S_h/S_w$)', color=color_scis, fontsize=12)
    ax2.tick_params(axis='y', labelcolor=color_scis)

    # Set initial base limits for the RIGHT axis
    base_y2_min = 0.0
    base_y2_max = 0.40
    ax2.set_ylim(base_y2_min, base_y2_max)

    # Plot Aerodynamic Boundaries directly from X_plot data (No Extrapolation to preserve exact curves)
    l4, = ax2.plot(xp.x_np, xp.Sh_S_array, color='black', linestyle='--', linewidth=1.5, label='Neutral Point')
    l5, = ax2.plot(xp.x_aft_limit, xp.Sh_S_array, color='#665191', linewidth=1.5, label='Aft Limit (Stability)')
    l6, = ax2.plot(xp.x_fwd_limit, xp.Sh_S_array, color='#2f4b7c', linewidth=1.5, label='Forward Limit (Control)')

    # --- Draw the Orange Connecting Line using exact variables calculated in X_plot.py ---
    curr_Sh_S = xp.current_Sh_S
    curr_x_fwd_aero = float(np.ravel(xp.x_fwd_curr)[0])
    curr_x_aft_aero = float(np.ravel(xp.x_np_curr - xp.static_margin)[0])

    l7, = ax2.plot([curr_x_fwd_aero, curr_x_aft_aero], [curr_Sh_S, curr_Sh_S],
                   color='#ff7c43', linewidth=2.0, marker='|', markeredgewidth=1.5, markersize=8,
                   label=f'Current Aero Limits ($S_h/S_w$={curr_Sh_S:.3f})')

    # --- 4. FORMATTING & LEGEND ---
    ax1.set_title("Combined Scissor Plot & CG Margins Envelope", fontsize=14, fontweight='bold', pad=15)
    ax1.grid(True, linestyle='-', color='#e0e0e0', linewidth=0.7)
    ax1.set_xlim(-0.4, 1.2)

    # Compile the legend handles
    ordered_handles = [l1, l2, fill_poly, l3, l6, l5, l4, l7]
    ordered_labels = [h.get_label() for h in ordered_handles]

    # Plot unified legend inside the plot
    ax1.legend(ordered_handles, ordered_labels, loc='lower left',
               frameon=True, framealpha=0.95, fontsize=9, edgecolor='#cccccc')

    # --- 5. INTERACTIVE SLIDERS ---
    # Define slider axes [left, bottom, width, height]
    ax_slider_left = fig.add_axes([0.15, 0.15, 0.7, 0.03])
    ax_slider_right = fig.add_axes([0.15, 0.08, 0.7, 0.03])

    # Left Axis Slider (Controls the Wing Position view)
    slider_left = Slider(
        ax=ax_slider_left,
        label='Shift Wing Pos. Axis',
        valmin=-0.2,
        valmax=0.2,
        valinit=0.0,
        color=color_cg
    )

    # Right Axis Slider (Controls the Scissor Plot view)
    slider_right = Slider(
        ax=ax_slider_right,
        label='Shift $S_h/S_w$ Axis',
        valmin=-0.4,
        valmax=0.4,
        valinit=0.0,
        color=color_scis
    )

    # Function to update the plot when the sliders move
    def update(val):
        offset_left = slider_left.val
        offset_right = slider_right.val

        # Shift the Y-limits
        ax1.set_ylim(base_y1_min + offset_left, base_y1_max + offset_left)
        ax2.set_ylim(base_y2_min + offset_right, base_y2_max + offset_right)
        fig.canvas.draw_idle()

    # Link both sliders to the update function
    slider_left.on_changed(update)
    slider_right.on_changed(update)

    # --- 6. ENVELOPE CLEARANCE CHECK (PASS/FAIL) ---
    print("\n" + "=" * 50)
    print("   AERODYNAMIC ENVELOPE CLEARANCE CHECK")
    print("=" * 50)

    # Calculate clearances (Positive = Safe / Negative = Exceedance)
    fwd_clearance = curr_fwd_margin - curr_x_fwd_aero
    aft_clearance = curr_x_aft_aero - curr_aft_margin

    if fwd_clearance >= 0 and aft_clearance >= 0:
        print("[PASS] The current CG envelope is strictly within aerodynamic limits.")
    else:
        print("[FAIL] The current CG envelope EXCEEDS aerodynamic limits.")

    print(f"\n  -> Fwd Aero Control Limit: {curr_x_fwd_aero:.4f} MAC")
    print(f"  -> Fwd CG Limit (w/ marg): {curr_fwd_margin:.4f} MAC  | Clearance: {fwd_clearance:+.4f} MAC")
    print(f"  -> Aft CG Limit (w/ marg): {curr_aft_margin:.4f} MAC  | Clearance: {aft_clearance:+.4f} MAC")
    print(f"  -> Aft Aero Stab Limit:    {curr_x_aft_aero:.4f} MAC")
    print("=" * 50 + "\n")

    plt.show()

    # Return both sliders so they aren't garbage collected
    return slider_left, slider_right


# =====================================================================
# EXECUTION
# =====================================================================
if __name__ == '__main__':
    # Sweeping from 10 to 30 ensures the envelope goes way off-screen for scrolling
    sliders = generate_combined_plot(min_lemacw=10.0, max_lemacw=30.0, num_points=100)