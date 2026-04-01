import Input as ip
import CG_positions as CG
import numpy as np
import speed_of_sound
import matplotlib.pyplot as plt

def get_flap_area_proportion(y_start, y_end, b, c_root, taper):
    b_half = b / 2.0
    c_tip = c_root * taper

    def get_chord(y):
        return c_root + ((c_tip - c_root) / b_half) * y

    c_start = get_chord(y_start)
    c_end = get_chord(y_end)

    flap_segment_area = 0.5 * (c_start + c_end) * (y_end - y_start)
    half_wing_area = 0.5 * (c_root + c_tip) * b_half

    return flap_segment_area / half_wing_area

MLW = 36968
# -------- INITIALIZATION & AERO CONSTANTS -----
a = speed_of_sound.get_atmosphere_properties(ip.altitude)[0]
rho_sealevel = 1.225
V = ip.M * a
CL_max = ip.CL_max

Vh_V = 1
x_h_LEMACNORM = ((ip.x_LEMACh + 0.25 * CG.c_mach) - ip.x_LEMACw) / CG.c_macw
eta_h = 0.95
eta_w = 0.95
static_margin = 0.05

print("\n" + "="*50)
print(" STABILITY CALCULATIONS & INTERMEDIATE VARIABLES ")
print("="*50)
print(f"Mach Number (M): {ip.M}")
print(f"Velocity (V): {V:.2f} m/s")
print(f"Speed of Sound (a): {a:.2f} m/s")

# --- Cl_ALPHAh Calculation --
V_h = Vh_V * V
M_h = V_h / a
beta = np.sqrt(1 - M_h ** 2)
A_h = ip.b_h ** 2 / ip.S_h
SWEEP_ANGLEh = np.radians(ip.SWEEP_ANGLEh)
taper_factor = (1 - ip.TAPER_RATIOh) / (1 + ip.TAPER_RATIOh)
tan_SWEEP_ANGLEh_halfchord = np.tan(SWEEP_ANGLEh) - (2 / A_h) * taper_factor
SWEEP_ANGLEh_halfchord = np.arctan(tan_SWEEP_ANGLEh_halfchord)

numerator = 2 * np.pi * A_h
term1 = (A_h * beta / eta_h) ** 2
term2 = 1 + (np.tan(SWEEP_ANGLEh_halfchord) ** 2) / (beta ** 2)
denominator = 2 + np.sqrt(4 + term1 * term2)
Cl_ALPHAh = numerator / denominator

print("\n--- 1. Tail Lift Curve Slope [Eq. 1] ---")
print(f"Tail Aspect Ratio (A_h): {A_h:.4f}")
print(f"Tail Compressibility Factor (beta): {beta:.4f}")
print(f"Tail Half-Chord Sweep (rad): {SWEEP_ANGLEh_halfchord:.4f}")
print(f"Tail Lift Curve Slope (Cl_ALPHAh): {Cl_ALPHAh:.4f} per rad")

# --- Cl_ALPHAw Calculation (CRUISE) ---
M_w = ip.M
beta_w = np.sqrt(1 - M_w ** 2)
A_w = ip.b_w ** 2 / ip.S_w
SWEEP_ANGLEw = np.radians(ip.SWEEP_ANGLEw)
TAPER_RATIOw = ip.TAPER_RATIOw
taper_factor_w = (1 - TAPER_RATIOw) / (1 + TAPER_RATIOw)
tan_SWEEP_ANGLEw_halfchord = np.tan(SWEEP_ANGLEw) - (2 / A_w) * taper_factor_w
SWEEP_ANGLEw_halfchord = np.arctan(tan_SWEEP_ANGLEw_halfchord)

numerator_w = 2 * np.pi * A_w
term1_w = (A_w * beta_w / eta_w) ** 2
term2_w = 1 + (np.tan(SWEEP_ANGLEw_halfchord) ** 2) / (beta_w ** 2)
denominator_w = 2 + np.sqrt(4 + term1_w * term2_w)
Cl_ALPHAw = numerator_w / denominator_w

print("\n--- 2. Wing Lift Curve Slope (Cruise) ---")
print(f"Wing Compressibility Factor (beta_w): {beta_w:.4f}")
print(f"Wing Lift Curve Slope (Cl_ALPHAw): {Cl_ALPHAw:.4f} per rad")

# --- Cl_ALPHAa_h (Aircraft Less Tail - CRUISE) ---
b_f = ip.d_fus
h_f = ip.d_fus
l_f = ip.l_fus
S_net = ip.S_w - ip.d_fus * ip.c_rw
interference_factor = 1 + 2.15 * (b_f / ip.b_w)
term1_A_h = Cl_ALPHAw * interference_factor * (S_net / ip.S_w)
term2_A_h = (np.pi / 2) * (b_f ** 2 / ip.S_w)
Cl_ALPHAa_h = term1_A_h + term2_A_h

print("\n--- 3. Aircraft-Less-Tail Lift Curve Slope (Cruise) ---")
print(f"  -> Wing Contribution: {term1_A_h:.4f} per rad")
print(f"  -> Fuselage Contribution: {term2_A_h:.4f} per rad")
print(f"Total Aircraft-less-tail Lift Curve Slope (Cl_ALPHAa_h): {Cl_ALPHAa_h:.4f} per rad")

# --- x_ac_LEMACNORM (Fuselage & Nacelle Effects - CRUISE) ---
x_acw_LEMACNORM = 0.3
y_root_to_mac = CG.y_macw - (ip.d_fus / 2)
delta_x_sweep = y_root_to_mac * np.tan(np.radians(ip.SWEEP_ANGLEw))
l_fn = ip.x_LEMACw - delta_x_sweep
c_gw = ip.S_w / ip.b_w
tan_sweep_quarter_chord = np.tan(SWEEP_ANGLEw) - (1 / A_w) * taper_factor_w
SWEEP_ANGLEw_quarterchord = np.arctan(tan_sweep_quarter_chord)

fuse_cont_1 = (1.8 * b_f * h_f * l_fn) / (Cl_ALPHAa_h * ip.S_w * CG.c_macw)
num_fuse_cont_2 = 0.273 * b_f * c_gw * (ip.b_w - b_f) * np.tan(SWEEP_ANGLEw_quarterchord)
den_fuse_cont_2 = (1 + TAPER_RATIOw) * (CG.c_macw ** 2) * (ip.b_w + 2.15 * b_f)
fuse_cont_2 = num_fuse_cont_2 / den_fuse_cont_2

n_nacelles = ip.n_nacelle
d_nac = ip.d_nac
x_quarter_mac = ip.x_LEMACw + 0.25 * CG.c_macw
l_n = x_quarter_mac - ip.x_startnacelle
k_n = -4.0 if ip.x_startnacelle < ip.x_LEMACw else -2.5

x_acn_LEMACNORM = n_nacelles * (k_n * (d_nac ** 2) * l_n) / (ip.S_w * CG.c_macw * Cl_ALPHAa_h)
x_acwf_LEMACNORM = x_acw_LEMACNORM - fuse_cont_1 + fuse_cont_2
x_ac_LEMACNORM = x_acn_LEMACNORM + x_acwf_LEMACNORM

print("\n--- 4a. Aerodynamic Center Shift (Cruise for Stability) ---")
print(f"  -> Base Wing AC (x_acw): {x_acw_LEMACNORM:.4f} MAC")
print(f"  -> Fuselage Contribution: {-fuse_cont_1 + fuse_cont_2:.4f} MAC")
print(f"  -> Nacelles Contribution: {x_acn_LEMACNORM:.4f} MAC")
print(f"Total Aircraft Aerodynamic Center (x_ac_LEMACNORM): {x_ac_LEMACNORM:.4f} MAC")

# =====================================================================
# --- LANDING CONDITIONS (M ≈ 0) FOR CONTROLLABILITY ---
# =====================================================================
beta_w_land = 1.0  # M effectively 0
term1_w_land = (A_w * beta_w_land / eta_w) ** 2
term2_w_land = 1 + (np.tan(SWEEP_ANGLEw_halfchord) ** 2) / (beta_w_land ** 2)
denominator_w_land = 2 + np.sqrt(4 + term1_w_land * term2_w_land)
Cl_ALPHAw_land = numerator_w / denominator_w_land

term1_A_h_land = Cl_ALPHAw_land * interference_factor * (S_net / ip.S_w)
Cl_ALPHAa_h_land = term1_A_h_land + term2_A_h

x_acw_LEMACNORM_land = 0.32
fuse_cont_1_land = (1.8 * b_f * h_f * l_fn) / (Cl_ALPHAa_h_land * ip.S_w * CG.c_macw)
x_acn_LEMACNORM_land = n_nacelles * (k_n * (d_nac ** 2) * l_n) / (ip.S_w * CG.c_macw * Cl_ALPHAa_h_land)

x_acwf_LEMACNORM_land = x_acw_LEMACNORM_land - fuse_cont_1_land + fuse_cont_2
x_ac_LEMACNORM_land = x_acn_LEMACNORM_land + x_acwf_LEMACNORM_land

print("\n--- 4b. Aerodynamic Center Shift (Landing for Control) ---")
print(f"Landing Wing Lift Curve Slope (Cl_ALPHAw_land): {Cl_ALPHAw_land:.4f}")
print(f"  -> Wing Lift Contribution: {term1_A_h_land:.4f} per rad")
print(f"  -> Fuselage Lift Contribution: {term2_A_h:.4f} per rad")
print(f"Total Landing Aircraft-Less-Tail Lift Curve Slope (Cl_ALPHAa_h_land): {Cl_ALPHAa_h_land:.4f} per rad")
print(f"  -> Landing Base Wing AC (x_acw_land): {x_acw_LEMACNORM_land:.4f} MAC")
print(f"  -> Landing Fuselage Contribution: {-fuse_cont_1_land + fuse_cont_2:.4f} MAC")
print(f"  -> Landing Nacelles Contribution: {x_acn_LEMACNORM_land:.4f} MAC")
print(f"Total Landing Aerodynamic Center (x_ac_LEMACNORM_land): {x_ac_LEMACNORM_land:.4f} MAC")

# --- C_m_ac Calculation (Using Landing Values) ---
C_m0 = ip.C_m0
CL_0 = ip.CL_0

cos_sweep_qc = np.cos(SWEEP_ANGLEw_quarterchord)
C_m_ac_w = C_m0 * (A_w * (cos_sweep_qc ** 2)) / (A_w + 2 * cos_sweep_qc)

term1_fus = 1 - ((2.5 * b_f) / l_f)
term2_fus = (np.pi * b_f * h_f * l_f) / (4 * ip.S_w * CG.c_macw)
term3_fus_land = CL_0 / Cl_ALPHAa_h_land
Delta_fus_C_m_ac_land = -1.8 * term1_fus * term2_fus * term3_fus_land

deltac_c_f = 0.4
c_f = 0.7
deltac_f = c_f * deltac_c_f
c_ratio = (deltac_f + CG.c_macw) / CG.c_macw
delta_cl_max_flaps = c_ratio * 1.6

mu_1 = 0.175
mu_2 = 0.55
mu_3 = 0.055
y_start = 1.29
y_end = 9.79
y_span = y_end - y_start
S_wf_S = get_flap_area_proportion(y_start, y_end, ip.b_w, ip.c_rw, ip.TAPER_RATIOw)

term1_cm = -mu_1 * delta_cl_max_flaps * c_ratio
term2_cm = -(CL_max + delta_cl_max_flaps * (1 - S_wf_S)) * (1/8) * c_ratio * (c_ratio - 1)
part1_cm = mu_2 * (term1_cm + term2_cm)
part2_cm = 0.7 * (A_w / (1 + 2/A_w)) * mu_3 * delta_cl_max_flaps * np.tan(SWEEP_ANGLEw_quarterchord)

Delta_C_m_1_4 = part1_cm + part2_cm
Delta_C_m_ac_HLD_land = Delta_C_m_1_4 - CL_max * (0.25 - x_ac_LEMACNORM_land)
C_m_ac_land = C_m_ac_w + Delta_fus_C_m_ac_land + Delta_C_m_ac_HLD_land

print("\n--- 5. Pitching Moment Calculation (Landing) ---")
print(f"  -> Wing Contribution (C_m_ac_w): {C_m_ac_w:.4f}")
print(f"  -> Fuselage Contribution Landing (Delta_fus_C_m_ac_land): {Delta_fus_C_m_ac_land:.4f}")
print(f"  -> Flap Delta C_m at AC Landing (Delta_C_m_ac_HLD_land): {Delta_C_m_ac_HLD_land:.4f}")
print(f"Total Landing Pitching Moment (C_m_ac_land): {C_m_ac_land:.4f}")

# --- de/da (Downwash Derivative) Calculation ---
x_qc_w = ip.x_LEMACw + 0.25 * CG.c_macw
x_qc_h = ip.x_LEMACh + 0.25 * CG.c_mach
l_H = x_qc_h - x_qc_w

r = l_H / (ip.b_w / 2)
m_tv = ip.m

Lambda_14 = SWEEP_ANGLEw_quarterchord
K_eps_Lambda = (0.1124 + 0.1265 * Lambda_14 + 0.1766 * Lambda_14**2) / (r**2) + (0.1024 / r) + 2
K_eps_Lambda_0 = (0.1124 / r**2) + (0.1024 / r) + 2

term1_de = (r / (r**2 + m_tv**2)) * (0.4876 / np.sqrt(r**2 + 0.6319 + m_tv**2))
term2_de_part1 = 1 + (r**2 / (r**2 + 0.7915 + 5.0734 * m_tv**2))**0.3113
term2_de_part2 = 1 - np.sqrt(m_tv**2 / (1 + m_tv**2))
term2_de = term2_de_part1 * term2_de_part2

de_da = (K_eps_Lambda / K_eps_Lambda_0) * (term1_de + term2_de) * (Cl_ALPHAw / (np.pi * A_w))

print("\n--- 6. Downwash Derivative ---")
print(f"Downwash Derivative (de_da): {de_da:.4f} rad/rad")

# --- SCISSOR PLOT CALCULATIONS ---
Sh_S_array = np.linspace(0.0, 0.40, 100)

# Aft Limit (Stability) - Uses Cruise AC
l_h_norm = x_h_LEMACNORM - x_acw_LEMACNORM
x_np = x_ac_LEMACNORM + (Cl_ALPHAh / Cl_ALPHAa_h) * (1 - de_da) * Sh_S_array * l_h_norm * (Vh_V ** 2)
x_aft_limit = x_np - static_margin

print("\n--- 7. Stability Boundary (Neutral Point) ---")
print(f"Static Margin limit: {static_margin}")

# Max Tail Lift Coefficient
CL_h_fixed = -0.35 * (A_h ** (1 / 3))

print("\n--- 8. Maximum Tail Lift Coefficient ---")
print(f"Max Tail Lift Coefficient (CL_h_fixed): {CL_h_fixed:.4f} (Assuming Fixed Stabilizer)")

W_landing = (MLW) * 9.81
S_h_dynamic = Sh_S_array * ip.S_w

V_approach_array = np.sqrt(W_landing / (0.5 * rho_sealevel * (ip.S_w * CL_max + S_h_dynamic * (Vh_V ** 2) * CL_h_fixed)))
V_approach_curr = np.sqrt(W_landing / (0.5 * rho_sealevel * (ip.S_w * CL_max + ip.S_h * (Vh_V ** 2) * CL_h_fixed)))

print("\n--- 9. Approach Speed Calculation ---")
print(f"Resulting V_approach:  {V_approach_curr:.2f} m/s ({V_approach_curr * 1.94384:.1f} knots)")

# Forward Limit (Control) - Uses Landing AC and Landing Cm
K_cont = (CL_h_fixed / CL_max) * (Vh_V ** 2) * Sh_S_array
C_term_land = x_ac_LEMACNORM_land - (C_m_ac_land / CL_max)
x_fwd_limit = (C_term_land + K_cont * x_h_LEMACNORM) / (1 + K_cont)

current_Sh_S = ip.S_h / ip.S_w
x_np_curr = x_ac_LEMACNORM + (Cl_ALPHAh / Cl_ALPHAa_h) * (1 - de_da) * current_Sh_S * l_h_norm * (Vh_V ** 2)

K_curr_cont = (CL_h_fixed / CL_max) * (Vh_V ** 2) * current_Sh_S
x_fwd_curr = (C_term_land + K_curr_cont * x_h_LEMACNORM) / (1 + K_curr_cont)

print("\n--- 10. Current Configuration Results ---")
print(f"Current Sh/S ratio: {current_Sh_S:.4f}")
print(f"Current Neutral Point (x_np_curr): {x_np_curr:.4f}")
print(f"Current Forward Limit (x_fwd_curr): {x_fwd_curr:.4f}")
print("="*50 + "\n")

# --- PLOTTING ---
if __name__ == '__main__':
    plt.figure(figsize=(8, 6))
    plt.plot(x_np, Sh_S_array, 'k--', label='Neutral Point (Cruise)')
    plt.plot(x_aft_limit, Sh_S_array, 'b-', label='Aft Limit (Stability)')
    plt.plot(x_fwd_limit, Sh_S_array, 'g-', label='Forward Limit (Control Landing)')

    plt.plot([x_fwd_curr, x_np_curr - static_margin], [current_Sh_S, current_Sh_S], 'r-o', linewidth=2,
             label='Current CG Range')

    plt.xlabel('x_cg / c_mac')
    plt.ylabel('S_h / S_w')
    plt.title('Scissor Plot')
    plt.xlim(-0.2, 1.0)
    plt.ylim(0.0, 0.4)
    plt.grid(True)
    plt.legend()
    plt.show()