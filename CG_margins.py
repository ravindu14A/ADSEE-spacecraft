import numpy as np
import matplotlib.pyplot as plt

# Import the necessary modules
import Input as ip
import CG_positions as cg
import potato_bandi as pb


def run_lemac_sweep(min_lemacw, max_lemacw, num_points=50):
    """
    Sweeps through a range of X_LEMACw values to find the corresponding
    forward and aft CG limits.
    """
    print(f"Starting X_LEMACw sweep from {min_lemacw} to {max_lemacw} with {num_points} points...")

    # 1. Setup Sweep Parameters
    # Generate an array of X_LEMACw values to test using the min and max
    x_lemac_array = np.linspace(min_lemacw, max_lemacw, num_points)

    # Pre-allocate lists to store the results
    fwd_cg_limits = []
    aft_cg_limits = []
    y_axis_ratios = []

    # 2. Execution Loop
    for x_lemac in x_lemac_array:
        # Step A: Get the updated OEW CG based on the current wing position
        # Accessing the dictionary output: ["from_nose"]["aircraft"]
        cg_results = cg.calculate_aircraft_cgs(x_lemac)
        current_x_oew = cg_results["from_nose"]["aircraft"]

        # Step B: Get the CG envelope limits for this specific wing/OEW configuration
        # potato_bandi returns: most_fwd_cg, most_aft_cg, fwd_limit_with_margin, aft_limit_with_margin
        # We set plot=False so it doesn't spawn individual potato diagrams
        _, _, fwd_margin, aft_margin = pb.calculate_cg_limits(
            X_OEW=current_x_oew,
            X_LEMAC=x_lemac,
            plot=False
        )

        # Step C: Store the data
        fwd_cg_limits.append(fwd_margin)
        aft_cg_limits.append(aft_margin)

        # The y-axis is the wing position normalized by the fuselage length
        y_axis_ratios.append(x_lemac / ip.l_fus)

    print("Sweep complete. Generating plot...")

    # 3. Plotting
    # Set to default light mode style
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot the FWD and AFT limits
    ax.plot(fwd_cg_limits, y_axis_ratios, color='blue', linewidth=2, label='FWD CG Limit (w/ Margin)')
    ax.plot(aft_cg_limits, y_axis_ratios, color='red', linewidth=2, label='AFT CG Limit (w/ Margin)')

    # Fill the area between the limits to represent the safe operational envelope
    ax.fill_betweenx(y_axis_ratios, fwd_cg_limits, aft_cg_limits, color='gray', alpha=0.15,
                     label='Allowable CG Envelope')

    # Formatting
    ax.set_title("Wing Position vs. CG Envelope Shift", fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel("CG Position ($x_{cg} / MAC$)", fontsize=12)
    ax.set_ylabel("Normalized Wing Position ($X_{LEMACw} / l_{fus}$)", fontsize=12)

    # Add grid and legend (standard white background for legend)
    ax.grid(True, alpha=0.5, linestyle='--')
    ax.legend(loc='upper right', frameon=True)

    plt.tight_layout()
    plt.show()


# =====================================================================
# EXECUTION
# =====================================================================
if __name__ == '__main__':
    # Define the minimum and maximum values of X_LEMACw to sweep.
    # Adjust these variables based on your aircraft's physical limits.
    MIN_X_LEMACW_TO_SWEEP = 17.0
    MAX_X_LEMACW_TO_SWEEP = 19.0

    run_lemac_sweep(min_lemacw=MIN_X_LEMACW_TO_SWEEP, max_lemacw=MAX_X_LEMACW_TO_SWEEP, num_points=100)