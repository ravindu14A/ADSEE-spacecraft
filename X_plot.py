import Input as ip
import CG_positions as CG
import numpy as np
import speed_of_sound
import matplotlib.pyplot as plt

MLW = 36968
# -------- INITIALIZATION & AERO CONSTANTS -----
a = speed_of_sound.get_atmosphere_properties(ip.altitude)[0]
rho_sealevel = 1.225
V = ip.M * a
V_landing = ip.V_landing
de_da = 0.3
Vh_V = 0.95
x_h_LEMACNORM = ((ip.x_LEMACh + 0.25 * CG.c_mach) - ip.x_LEMACw) / CG.c_macw
eta_h = 0.95
eta_w = 0.95
static_margin = 0.05

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

# --- Cl_ALPHAw Calculation ---
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

# --- Cl_ALPHAa_h (Aircraft Less Tail) ---
b_f = ip.d_fus
h_f = ip.d_fus
l_f = ip.l_fus
S_net = ip.S_w - ip.d_fus * ip.c_rw
interference_factor = 1 + 2.15 * (b_f / ip.b_w)
term1_A_h = Cl_ALPHAw * interference_factor * (S_net / ip.S_w)
term2_A_h = (np.pi / 2) * (b_f ** 2 / ip.S_w)
Cl_ALPHAa_h = term1_A_h + term2_A_h

# --- x_ac_LEMACNORM (Fuselage & Nacelle Effects) ---
x_acw_LEMACNORM = 0.25
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

# --- C_m_ac Calculation ---
C_m0 = ip.C_m0
CL_0 = ip.CL_0

# Wing Contribution
cos_sweep_qc = np.cos(SWEEP_ANGLEw_quarterchord)
C_m_ac_w = C_m0 * (A_w * (cos_sweep_qc ** 2)) / (A_w + 2 * cos_sweep_qc)

# Fuselage Contribution
term1_fus = 1 - ((2.5 * b_f) / l_f)
term2_fus = (np.pi * b_f * h_f * l_f) / (4 * ip.S_w * CG.c_macw)
term3_fus = CL_0 / Cl_ALPHAa_h
Delta_fus_C_m_ac = -1.8 * term1_fus * term2_fus * term3_fus

# Total Pitching Moment Coefficient (Neglecting Flaps & Nacelle)
C_m_ac = C_m_ac_w + Delta_fus_C_m_ac

# --- SCISSOR PLOT CALCULATIONS ---
Sh_S_array = np.linspace(0.0, 0.40, 100)

# Stability Boundary
K_stab = (Cl_ALPHAh / Cl_ALPHAa_h) * (1 - de_da) * (Vh_V ** 2) * Sh_S_array
x_np = (x_ac_LEMACNORM + K_stab * x_h_LEMACNORM) / (1 + K_stab)
x_aft_limit = x_np - static_margin

# Control Boundary
CL_h_fixed = -0.35 * (A_h ** (1 / 3))

# Dynamic Pressures
q_landing = 0.5 * rho_sealevel * V_landing ** 2
q_h_landing = 0.5 * rho_sealevel * (Vh_V * V_landing) ** 2
W_landing = (MLW) * 9.81

# Array representing the tail area for each point on the y-axis
S_h_dynamic = Sh_S_array * ip.S_w

# Dynamic array for the wing-body lift required at each tail size
CL_A_h_array = (W_landing - q_h_landing * S_h_dynamic * CL_h_fixed) / (q_landing * ip.S_w)

# --- NEW: Specific CL_A_h at selected Input S_h ---
CL_A_h = (W_landing - q_h_landing * ip.S_h * CL_h_fixed) / (q_landing * ip.S_w)
print(f"CL_A_h at selected input values (S_h = {ip.S_h}): {CL_A_h:.4f}")

K_cont = (CL_h_fixed / CL_A_h_array) * (Vh_V ** 2) * Sh_S_array
C_term = x_ac_LEMACNORM - (C_m_ac / CL_A_h_array)
x_fwd_limit = (C_term + K_cont * x_h_LEMACNORM) / (1 + K_cont)

# Current config points
current_Sh_S = ip.S_h / ip.S_w
K_curr_stab = (Cl_ALPHAh / Cl_ALPHAa_h) * (1 - de_da) * (Vh_V ** 2) * current_Sh_S
x_np_curr = (x_ac_LEMACNORM + K_curr_stab * x_h_LEMACNORM) / (1 + K_curr_stab)

# Current point scalar calculation using the actual ip.S_h (Reusing the new variable)
CL_A_h_curr = CL_A_h
K_curr_cont = (CL_h_fixed / CL_A_h_curr) * (Vh_V ** 2) * current_Sh_S
x_fwd_curr = (C_term[0] * 0 + x_ac_LEMACNORM - (C_m_ac / CL_A_h_curr) + K_curr_cont * x_h_LEMACNORM) / (1 + K_curr_cont)

# --- PLOTTING ---
if __name__ == '__main__':
    plt.figure(figsize=(8, 6))
    plt.plot(x_np, Sh_S_array, 'k--', label='Neutral Point')
    plt.plot(x_aft_limit, Sh_S_array, 'b-', label='Aft Limit (Stability)')
    plt.plot(x_fwd_limit, Sh_S_array, 'g-', label='Forward Limit (Control)')

    # Range bar for current S_h/S
    plt.plot([x_fwd_curr, x_np_curr - static_margin], [current_Sh_S, current_Sh_S], 'r-o', linewidth=2,
             label='Current CG Range')

    plt.xlabel('x_cg / c_mac')
    plt.ylabel('S_h / S')
    plt.title('Scissor Plot')
    plt.xlim(-0.2, 1.0)
    plt.ylim(0.0, 0.4)
    plt.grid(True)
    plt.legend()
    plt.show()