import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.widgets import Slider

# Import your core modules
import Input_updated as ip
import CG_positions_updated as cg
import potato_bandi_updated as pb

# Import the X-plot data
import X_plot_updated as xp

# =====================================================================
# OPTIMIZATION FLAG
# =====================================================================
OPTIMIZE = False  # Toggle this to automatically find the optimum LEMAC and Sh/Sw


# =====================================================================


def generate_combined_plot(min_lemacw=10.0, max_lemacw=30.0, num_points=80):
    # Sweeping a massive range (10m to 30m) so you never run out of envelope when sliding
    print("Calculating Extended CG Margins...")

    # 1. Calculate CG Margins Sweep
    x_lemac_array = np.linspace(min_lemacw, max_lemacw, num_points)
    fwd_cg_limits = []
    aft_cg_limits = []
    y_axis_ratios = []

    for x_lemac in x_lemac_array:
        cg_results = cg.calculate_aircraft_cgs(x_lemac)
        current_x_oew = cg_results["from_nose"]["aircraft"]

        # STRICT EXTRACTION: Will throw KeyError if "Wing" does not exist
        current_x_wing = cg_results["from_nose"]["components"]["Wing"]

        _, _, fwd_margin, aft_margin = pb.calculate_cg_limits(
            X_OEW=current_x_oew,
            X_LEMAC=x_lemac,
            X_FUEL=current_x_wing,
            plot=False
        )

        fwd_cg_limits.append(fwd_margin)
        aft_cg_limits.append(aft_margin)
        y_axis_ratios.append(x_lemac / ip.l_fus)

    # --- AERODYNAMIC EXTRAPOLATION LOGIC ---
    # Calculate slopes to extrapolate accurately based on existing xp data
    def extrapolate(x_pts, y_pts, target_y):
        slope, intercept = np.polyfit(y_pts, x_pts, 1)
        return slope * target_y + intercept

    # We need the direct polynomial coefficients to solve for Sh/Sw
    slope_fwd, int_fwd = np.polyfit(xp.Sh_S_array, xp.x_fwd_limit, 1)
    slope_aft, int_aft = np.polyfit(xp.Sh_S_array, xp.x_aft_limit, 1)

    # --- 2. OPTIMIZATION LOGIC ---
    if OPTIMIZE:
        print("\nOptimizing LEMAC for minimum Horizontal Tail size...")

        # Increase resolution for precise optimization without running slow calculations
        fine_lemac = np.linspace(min_lemacw, max_lemacw, 2000)
        fine_fwd = np.interp(fine_lemac, x_lemac_array, fwd_cg_limits)
        fine_aft = np.interp(fine_lemac, x_lemac_array, aft_cg_limits)

        # Required Sh/Sw for each limit: x = slope * y + intercept => y = (x - intercept) / slope
        req_sh_fwd = (fine_fwd - int_fwd) / slope_fwd
        req_sh_aft = (fine_aft - int_aft) / slope_aft

        # The minimum required tail size at any LEMAC is the bottleneck (max) of the two limits
        req_sh_max = np.maximum(req_sh_fwd, req_sh_aft)

        # The optimal LEMAC is where this required maximum tail size is at its absolute minimum
        opt_idx = np.argmin(req_sh_max)

        active_lemac = fine_lemac[opt_idx]
        active_sh_s = req_sh_max[opt_idx]

        lemac_change = active_lemac - ip.x_LEMACw
        sh_change = active_sh_s - xp.current_Sh_S

        print("=" * 50)
        print("   OPTIMIZATION RESULTS")
        print("=" * 50)
        print(f"Optimal X_LEMACw: {active_lemac:.4f} m")
        print(f"Optimal S_h/S_w:  {active_sh_s:.4f}")
        print(f"LEMAC CHANGE:     {lemac_change:+.4f} m")
        print(f"S_h/S_w CHANGE:   {sh_change:+.4f}")

        # If the input file has the main wing area (S), calculate absolute area change
        if hasattr(ip, 'S'):
            print(f"S_h AREA CHANGE:  {sh_change * ip.S:+.4f} m^2")
        print("=" * 50 + "\n")

    else:
        active_lemac = ip.x_LEMACw
        active_sh_s = xp.current_Sh_S

    # --- 3. GET SPECIFIC LIMITS FOR THE ACTIVE CONFIGURATION ---
    curr_cg_results = cg.calculate_aircraft_cgs(active_lemac)
    curr_x_oew = curr_cg_results["from_nose"]["aircraft"]
    curr_x_wing = curr_cg_results["from_nose"]["components"]["Wing"]

    _, _, curr_fwd_margin, curr_aft_margin = pb.calculate_cg_limits(
        X_OEW=curr_x_oew,
        X_LEMAC=active_lemac,
        X_FUEL=curr_x_wing,
        plot=False
    )
    curr_lemac_ratio = active_lemac / ip.l_fus

    print("Generating Combined Overlay Plot...")

    # --- 4. SETUP FIGURE AND AXES ---
    plt.style.use('default')
    fig, ax1 = plt.subplots(figsize=(10, 8))

    # Make room at the bottom for TWO sliders
    fig.subplots_adjust(bottom=0.30)

    # --- AXIS 1: CG MARGINS (Left Y-Axis) ---
    color_cg = '#1f77b4'
    ax1.set_xlabel('CG Position ($x_{cg} / MAC$)', fontsize=12)
    ax1.set_ylabel('Normalized Wing Position ($X_{LEMACw} / l_{fus}$)', color=color_cg, fontsize=12)
    ax1.tick_params(axis='y', labelcolor=color_cg)

    # Plot Envelope
    l1, = ax1.plot(fwd_cg_limits, y_axis_ratios, color='#003f5c', linewidth=1.5, label='FWD CG Limit (w/ Margin)')
    l2, = ax1.plot(aft_cg_limits, y_axis_ratios, color='#d45087', linewidth=1.5, linestyle='-',
                   label='AFT CG Limit (w/ Margin)')

    ax1.fill_betweenx(y_axis_ratios, fwd_cg_limits, aft_cg_limits, color='#eaeaea', alpha=0.7)
    fill_poly = Patch(facecolor='#eaeaea', edgecolor='none', alpha=0.7, label='Allowable CG Envelope')

    # Draw the Red Connecting Line for Active LEMAC
    config_label = "Optimal Config" if OPTIMIZE else "Current Config"
    l3, = ax1.plot([curr_fwd_margin, curr_aft_margin], [curr_lemac_ratio, curr_lemac_ratio],
                   color='#d45087', linewidth=2.0, marker='|', markeredgewidth=1.5, markersize=8,
                   label=f'{config_label} (LEMAC={active_lemac:.2f}m)')

    # Set initial base limits centered on the active setup
    base_y1_min = (active_lemac - 3.0) / ip.l_fus
    base_y1_max = (active_lemac + 3.0) / ip.l_fus
    ax1.set_ylim(base_y1_min, base_y1_max)

    # --- AXIS 2: SCISSOR PLOT (Right Y-Axis) ---
    ax2 = ax1.twinx()
    color_scis = '#2f4b7c'
    ax2.set_ylabel('Horizontal Tail Area Ratio ($S_h / S_w$)', color=color_scis, fontsize=12)
    ax2.tick_params(axis='y', labelcolor=color_scis)

    # EXTEND SCISSOR PLOT DATA RANGE
    ext_Sh_S_array = np.linspace(-2.0, 2.0, 500)
    x_np_ext = extrapolate(xp.x_np, xp.Sh_S_array, ext_Sh_S_array)
    x_aft_ext = extrapolate(xp.x_aft_limit, xp.Sh_S_array, ext_Sh_S_array)
    x_fwd_ext = extrapolate(xp.x_fwd_limit, xp.Sh_S_array, ext_Sh_S_array)

    # Set initial base limits centered on the active setup
    base_y2_min = active_sh_s - 0.2
    base_y2_max = active_sh_s + 0.2
    ax2.set_ylim(base_y2_min, base_y2_max)

    # Plot Extended Aerodynamic Boundaries
    l4, = ax2.plot(x_np_ext, ext_Sh_S_array, color='black', linestyle='--', linewidth=1.5, label='Neutral Point')
    l5, = ax2.plot(x_aft_ext, ext_Sh_S_array, color='#665191', linewidth=1.5, label='Aft Limit (Stability)')
    l6, = ax2.plot(x_fwd_ext, ext_Sh_S_array, color='#2f4b7c', linewidth=1.5, label='Forward Limit (Control)')

    # Calculate exact positions for the active S_h/S_w line
    curr_x_fwd_aero = extrapolate(xp.x_fwd_limit, xp.Sh_S_array, active_sh_s)
    curr_x_aft_aero = extrapolate(xp.x_aft_limit, xp.Sh_S_array, active_sh_s)

    l7, = ax2.plot([curr_x_fwd_aero, curr_x_aft_aero], [active_sh_s, active_sh_s],
                   color='#ff7c43', linewidth=2.0, marker='|', markeredgewidth=1.5, markersize=8,
                   label=f'{config_label} Aero Limits ($S_h/S_w$={active_sh_s:.3f})')

    # --- 5. FORMATTING & LEGEND ---
    title_text = "Combined Scissor Plot & CG Margins Envelope"
    if OPTIMIZE:
        title_text += " [OPTIMIZED]"

    ax1.set_title(title_text, fontsize=14, fontweight='bold', pad=15)
    ax1.grid(True, linestyle='-', color='#e0e0e0', linewidth=0.7)
    ax1.set_xlim(-0.4, 1.4)

    # Combine legends and place inside the plot
    ordered_handles = [l1, l2, fill_poly, l3, l6, l5, l4, l7]
    ordered_labels = [h.get_label() for h in ordered_handles]

    ax1.legend(ordered_handles, ordered_labels, loc='lower left',
               frameon=True, framealpha=0.95, fontsize=9, edgecolor='#cccccc')

    # --- 6. INTERACTIVE SLIDERS ---
    ax_slider_left = fig.add_axes([0.15, 0.15, 0.7, 0.03])
    ax_slider_right = fig.add_axes([0.15, 0.08, 0.7, 0.03])

    slider_left = Slider(
        ax=ax_slider_left,
        label='Shift Wing Pos. Axis',
        valmin=-1.0,
        valmax=1.0,
        valinit=0.0,
        color=color_cg
    )

    slider_right = Slider(
        ax=ax_slider_right,
        label='Shift $S_h/S_w$ Axis',
        valmin=-1.0,
        valmax=1.0,
        valinit=0.0,
        color=color_scis
    )

    def update(val):
        offset_left = slider_left.val
        offset_right = slider_right.val
        ax1.set_ylim(base_y1_min + offset_left, base_y1_max + offset_left)
        ax2.set_ylim(base_y2_min + offset_right, base_y2_max + offset_right)
        fig.canvas.draw_idle()

    slider_left.on_changed(update)
    slider_right.on_changed(update)

    # --- 7. ENVELOPE CLEARANCE CHECK (PASS/FAIL) ---
    print("\n" + "=" * 50)
    print("   AERODYNAMIC ENVELOPE CLEARANCE CHECK")
    print("=" * 50)

    fwd_clearance = curr_fwd_margin - curr_x_fwd_aero
    aft_clearance = curr_x_aft_aero - curr_aft_margin

    if fwd_clearance >= -1e-4 and aft_clearance >= -1e-4:  # Added small tolerance for floating point math
        print("[PASS] The current CG envelope is strictly within aerodynamic limits.")
    else:
        print("[FAIL] The current CG envelope EXCEEDS aerodynamic limits.")

    print(f"\n  -> Fwd Aero Control Limit: {curr_x_fwd_aero:.4f} MAC")
    print(f"  -> Fwd CG Limit (w/ marg): {curr_fwd_margin:.4f} MAC  | Clearance: {fwd_clearance:+.4f} MAC")
    print(f"  -> Aft CG Limit (w/ marg): {curr_aft_margin:.4f} MAC  | Clearance: {aft_clearance:+.4f} MAC")
    print(f"  -> Aft Aero Stab Limit:    {curr_x_aft_aero:.4f} MAC")
    print("=" * 50 + "\n")

    plt.show()

    return slider_left, slider_right


# =====================================================================
# EXECUTION
# =====================================================================
if __name__ == '__main__':
    sliders = generate_combined_plot(min_lemacw=10.0, max_lemacw=30.0, num_points=80)