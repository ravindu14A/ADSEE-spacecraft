import numpy as np
import importlib

# Import your core modules
import Input_updated as ip
import CG_positions_updated as cg
import potato_bandi_updated as pb
import speed_of_sound

# =====================================================================
# MASTER TOGGLES
# =====================================================================
APPLY_TAIL_MASS_PENALTY = False
# =====================================================================

# Capture Baseline True Values before the loop modifies anything
ORIG_Sh = ip.S_h
ORIG_bh = ip.b_h
ORIG_Ah = (ORIG_bh ** 2) / ORIG_Sh
ORIG_Wh = cg.WEIGHT_HORIZONTAL_TAIL
ORIG_EOW = ip.EOW
ORIG_W_fuel = ip.W_fuel
ORIG_x_cgh = cg.x_cgh
ORIG_x_LEMACh = ip.x_LEMACh
ORIG_c_mach = cg.c_mach


def evaluate_aero_limits(S_h, x_LEMACw, x_LEMACh):
    """
    Dynamically calculates the aerodynamic scissor limits.
    """
    a = speed_of_sound.get_atmosphere_properties(ip.altitude)[0]
    V = ip.M * a
    rho_sealevel = 1.225
    CL_max = 2.6
    de_da = 0.3
    Vh_V = 0.95
    eta_h = 0.95
    eta_w = 0.95
    static_margin = 0.05

    scale_factor = np.sqrt(S_h / ORIG_Sh)
    current_c_mach = ORIG_c_mach * scale_factor
    x_h_LEMACNORM = ((x_LEMACh + 0.25 * current_c_mach) - x_LEMACw) / cg.c_macw
    A_h = ip.b_h ** 2 / S_h

    V_h = Vh_V * V
    M_h = V_h / a
    beta = np.sqrt(1 - M_h ** 2)
    taper_factor = (1 - ip.TAPER_RATIOh) / (1 + ip.TAPER_RATIOh)
    tan_SWEEPh = np.tan(np.radians(ip.SWEEP_ANGLEh)) - (2 / A_h) * taper_factor
    Cl_ALPHAh = (2 * np.pi * A_h) / (2 + np.sqrt(4 + (A_h * beta / eta_h) ** 2 * (1 + (tan_SWEEPh ** 2) / (beta ** 2))))

    A_w = (ip.b_w ** 2 / ip.S_w) * 1.25
    beta_w = np.sqrt(1 - ip.M ** 2)
    taper_factor_w = (1 - ip.TAPER_RATIOw) / (1 + ip.TAPER_RATIOw)
    tan_SWEEPw = np.tan(np.radians(ip.SWEEP_ANGLEw)) - (2 / A_w) * taper_factor_w
    Cl_ALPHAw = (2 * np.pi * A_w) / (
                2 + np.sqrt(4 + (A_w * beta_w / eta_w) ** 2 * (1 + (tan_SWEEPw ** 2) / (beta_w ** 2))))

    b_f, h_f, l_f = ip.d_fus, ip.d_fus, ip.l_fus
    S_net = ip.S_w - b_f * ip.c_rw
    Cl_ALPHAa_h = Cl_ALPHAw * (1 + 2.15 * (b_f / ip.b_w)) * (S_net / ip.S_w) + (np.pi / 2) * (b_f ** 2 / ip.S_w)

    delta_x_sweep = (cg.y_macw - (b_f / 2)) * np.tan(np.radians(ip.SWEEP_ANGLEw))
    l_fn = x_LEMACw - delta_x_sweep
    fuse_cont_1 = (1.8 * b_f * h_f * l_fn) / (Cl_ALPHAa_h * ip.S_w * cg.c_macw)
    num_fuse_cont_2 = 0.273 * b_f * (ip.S_w / ip.b_w) * (ip.b_w - b_f) * tan_SWEEPw
    fuse_cont_2 = num_fuse_cont_2 / ((1 + ip.TAPER_RATIOw) * (cg.c_macw ** 2) * (ip.b_w + 2.15 * b_f))

    x_acn_LEMACNORM = ip.n_nacelle * (-4.0 * (ip.d_nac ** 2) * (x_LEMACw + 0.25 * cg.c_macw - ip.x_startnacelle)) / (
                ip.S_w * cg.c_macw * Cl_ALPHAa_h)
    x_ac_LEMACNORM = x_acn_LEMACNORM + (0.25 - fuse_cont_1 + fuse_cont_2)

    C_m_ac_w = ip.C_m0 * (A_w * (np.cos(np.arctan(tan_SWEEPw)) ** 2)) / (A_w + 2 * np.cos(np.arctan(tan_SWEEPw)))
    Delta_fus_C_m_ac = -1.8 * (1 - ((2.5 * b_f) / l_f)) * ((np.pi * b_f * h_f * l_f) / (4 * ip.S_w * cg.c_macw)) * (
                ip.CL_0 / Cl_ALPHAa_h)
    C_m_ac = C_m_ac_w + Delta_fus_C_m_ac

    current_Sh_S = S_h / ip.S_w
    CL_h_fixed = -0.35 * (A_h ** (1 / 3))

    K_stab = (Cl_ALPHAh / Cl_ALPHAa_h) * (1 - de_da) * (Vh_V ** 2) * current_Sh_S
    x_aft_aero = ((x_ac_LEMACNORM + K_stab * x_h_LEMACNORM) / (1 + K_stab)) - static_margin

    K_cont = (CL_h_fixed / CL_max) * (Vh_V ** 2) * current_Sh_S
    x_fwd_aero = ((x_ac_LEMACNORM - (C_m_ac / CL_max)) + K_cont * x_h_LEMACNORM) / (1 + K_cont)

    return x_fwd_aero, x_aft_aero


def run_optimizer():
    print("Initializing Soft-Constraint Scorer (Nose Gear Loads Ignored)...")
    print("Objective: Maximize constraints passed with smallest gap to failures.\n")

    # --- WIDENED DESIGN SPACE ---
    lemac_options = np.arange(12.0, 26.0, 0.5)
    Sh_options = np.arange(15.0, 45.0, 0.5)
    x_LEMACh_options = np.arange(30.0, 38.0, 0.5)

    x_MG_options = np.arange(14.0, 26.0, 0.5)
    y_MG_options = np.arange(1.0, 5.0, 0.5)
    x_NW_options = np.arange(2.0, 6.0, 0.5)

    perfect_configs = []

    # Track the "Best Failed" config
    max_passes = -1
    min_error = float('inf')
    best_failed_config = None

    for x_LEMACw in lemac_options:
        cg_results_base = cg.calculate_aircraft_cgs(x_LEMACw)
        x_oew_base = cg_results_base["from_nose"]["aircraft"]
        x_wing = cg_results_base["from_nose"]["components"]["Wing"]

        c_local = ip.c_rw * (1 - (1 - ip.TAPER_RATIOw) * 0.35)
        x_rear_spar_abs = x_LEMACw + cg.distance_LEMAC_to_local_LE + (ip.rear_spar_fraction * c_local)

        for x_LEMACh in x_LEMACh_options:
            current_x_cgh = x_LEMACh + cg.x_cgh_relative

            for S_h in Sh_options:
                # Mass & Geometry
                scale_factor = np.sqrt(S_h / ORIG_Sh)
                ip.b_h = ORIG_bh * scale_factor
                ip.x_LEMACh = x_LEMACh

                if APPLY_TAIL_MASS_PENALTY:
                    new_Wh = ORIG_Wh * (S_h / ORIG_Sh)
                else:
                    new_Wh = ORIG_Wh

                delta_Wh = new_Wh - ORIG_Wh
                current_EOW = ORIG_EOW + delta_Wh
                current_W_fuel = ORIG_W_fuel - delta_Wh
                delta_moment = (new_Wh * current_x_cgh) - (ORIG_Wh * ORIG_x_cgh)
                current_x_oew = ((x_oew_base * ORIG_EOW) + delta_moment) / current_EOW

                ip.S_h = S_h
                ip.EOW = current_EOW
                ip.W_fuel = current_W_fuel

                # AERO CHECK (Done once per Sh loop to save processing time)
                _, _, fwd_cg_mac, aft_cg_mac = pb.calculate_cg_limits(current_x_oew, x_LEMACw, x_wing, plot=False)
                x_fwd_aero, x_aft_aero = evaluate_aero_limits(S_h, x_LEMACw, x_LEMACh)

                aero_passes = 0
                aero_error = 0.0
                aero_failures = []

                # 1. Fwd Aero
                fwd_gap = x_fwd_aero - fwd_cg_mac
                if fwd_gap <= 0:
                    aero_passes += 1
                else:
                    aero_error += fwd_gap * 10  # Weighted so MAC aligns with meters/degrees
                    aero_failures.append(f"Fwd Aero Missed by +{fwd_gap:.4f} MAC")

                # 2. Aft Aero
                aft_gap = aft_cg_mac - x_aft_aero
                if aft_gap <= 0:
                    aero_passes += 1
                else:
                    aero_error += aft_gap * 10
                    aero_failures.append(f"Aft Aero Missed by +{aft_gap:.4f} MAC")

                x_cg_fwd_abs = x_LEMACw + (fwd_cg_mac * cg.c_macw)
                x_cg_aft_abs = x_LEMACw + (aft_cg_mac * cg.c_macw)

                # GEAR LOOPS
                for x_MG in x_MG_options:
                    for y_MG in y_MG_options:
                        # Hard Filter: Must be mountable
                        is_near_spar = abs(x_MG - x_rear_spar_abs) <= 1.0
                        is_fuselage_mounted = y_MG <= 1.5
                        if not (is_near_spar or is_fuselage_mounted):
                            continue

                        for x_NW in x_NW_options:
                            # Start with the aero score
                            passes = aero_passes
                            error = aero_error
                            failures = list(aero_failures)

                            # 3. Static Tip Over
                            tip_gap = x_cg_aft_abs - x_MG
                            if tip_gap < 0:
                                passes += 1
                            else:
                                error += tip_gap
                                failures.append(f"Static Tip Missed by +{tip_gap:.2f} m")

                            # 4. Theta Clearance
                            beta_aft = np.rad2deg(np.arctan((x_MG - x_cg_aft_abs) / ip.z_cg))
                            theta_gap = ip.theta - beta_aft
                            if theta_gap < 0:
                                passes += 1
                            else:
                                error += theta_gap * 0.1
                                failures.append(f"Theta Missed by +{theta_gap:.2f} deg")

                            # 5. Dynamic Tip Over
                            alpha = np.arctan(y_MG / (x_MG - x_NW))
                            c_val = (x_cg_aft_abs - x_NW) * np.sin(alpha)

                            # Prevent math errors if CG is in front of NW (physically absurd but possible in math sweep)
                            if c_val > 0:
                                lamb = np.rad2deg(np.arctan(ip.z_cg / c_val))
                                lamb_gap = lamb - 55.0
                                if lamb_gap < 0:
                                    passes += 1
                                else:
                                    error += lamb_gap * 0.1
                                    failures.append(f"Dynamic Tip Missed by +{lamb_gap:.2f} deg")
                            else:
                                error += 50.0  # Massive penalty for invalid physics
                                failures.append("CG ahead of Nose Gear (Invalid)")

                            # --- SCORING EVALUATION ---
                            config_data = {
                                'S_h': S_h, 'LEMACw': x_LEMACw, 'LEMACh': x_LEMACh,
                                'x_MG': x_MG, 'y_MG': y_MG, 'x_NW': x_NW,
                                'Mount': "Fuselage" if is_fuselage_mounted else "Wing Spar",
                                'Passes': passes, 'Error': error, 'Failures': failures
                            }

                            if passes == 5:
                                perfect_configs.append(config_data)
                            else:
                                # Overwrite if this failure is closer to succeeding than the last best one
                                if passes > max_passes or (passes == max_passes and error < min_error):
                                    max_passes = passes
                                    min_error = error
                                    best_failed_config = config_data

    print("\nOptimization Complete.")

    # --- PRINT OUT RESULTS ---
    if len(perfect_configs) > 0:
        # Sort perfects by smallest tail (S_h)
        best = sorted(perfect_configs, key=lambda c: c['S_h'])[0]
        title = "PERFECT CONFIGURATION FOUND (5/5 Passed)"
    else:
        best = best_failed_config
        title = f"OPTIMUM 'CLOSEST' CONFIGURATION FOUND ({best['Passes']}/5 Passed)"

    print("\n" + "★" * 65)
    print(f"   {title}")
    print("★" * 65)
    print(f" -> Horizontal Tail Area (S_h): {best['S_h']:.2f} m^2")
    print(f" -> Wing Position (x_LEMACw):   {best['LEMACw']:.2f} m")
    print(f" -> Tail Position (x_LEMACh):   {best['LEMACh']:.2f} m")
    print(f" -> Main Gear X (x_MG):         {best['x_MG']:.2f} m  [{best['Mount']}]")
    print(f" -> Main Gear Y (y_MG):         {best['y_MG']:.2f} m")
    print(f" -> Nose Gear X (x_NW):         {best['x_NW']:.2f} m")
    print("-" * 65)

    if best['Passes'] == 5:
        print("  All physical and aerodynamic constraints satisfied successfully.")
    else:
        print(f"  FAILED CONSTRAINTS (Smallest calculated gap: {best['Error']:.2f} penalty pts)")
        for fail in best['Failures']:
            print(f"    [X] {fail}")
    print("★" * 65 + "\n")


if __name__ == '__main__':
    run_optimizer()