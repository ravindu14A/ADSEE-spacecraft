import CG_positions as CG
import Input as ip
import numpy as np

# ------------------------------------
# CG LIMITS
# ------------------------------------
x_cg_aft = 21
x_cg_fwd = 20

# ------------------------------------
# THETA CLEARANCE
# ------------------------------------
x_MG = ip.x_MG
z_cg = ip.z_cg
theta = ip.theta

# Tip-back is only a risk when the CG is furthest aft.
delta_x_MGtoCG_aft = x_MG - x_cg_aft
beta_aft = np.rad2deg(np.arctan(delta_x_MGtoCG_aft / z_cg))

# ------------------------------------
# NOSE WHEEL WEIGHT
# ------------------------------------
MTOW = ip.MTOW
x_NW = ip.x_NW
W_total = MTOW * 9.81

# Function to calculate nose wheel force
def calculate_F_NW(cg_position):
    return W_total * (x_MG - cg_position) / (x_MG - x_NW)

# Calculate forces at both operational extremes
F_NW_fwd = calculate_F_NW(x_cg_fwd)
F_NW_aft = calculate_F_NW(x_cg_aft)

# Convert to percentages of total weight
pct_fwd = (F_NW_fwd / W_total) * 100
pct_aft = (F_NW_aft / W_total) * 100

# ------------------------------------
# TIPPING REQUIREMENT
# ------------------------------------
# Static stability
y_MG = ip.y_MG
alpha = np.arctan(y_MG / (x_MG - x_NW))  #technically we should use this but tbh we dont need it since we dont have CG in Y direction
c = (x_cg_aft - x_NW) * np.sin(alpha)

# ------------------------------------
# WING CLEARANCE
# ------------------------------------
# Dynamic stability
lamb = np.rad2deg(np.arctan(z_cg / c))

# ------------------------------------
# TIP BACK REQUIREMENT
# ------------------------------------
# ------------------------------------
# REQUIREMENT CHECKS & OUTPUT
# ------------------------------------

print("--- STABILITY & CONTROL CHECKS ---")

# 1. Theta Clearance Check
if beta_aft > theta:
    print(f'[PASS] Theta clearance | Theta = {theta} deg, Beta (Aft CG) = {beta_aft:.4f} deg')
else:
    print(f'[FAIL] Theta clearance | Theta = {theta} deg, Beta (Aft CG) = {beta_aft:.4f} deg')

# 2. Nose Controllability Check (Requires > 8%)
if pct_aft > 8.0:
    print(f'[PASS] Nose controllability (Min Weight) | F_NW (Aft CG) = {pct_aft:.4f}% MTOW')
else:
    print(f'[FAIL] Nose controllability (Min Weight) | F_NW (Aft CG) = {pct_aft:.4f}% MTOW')

# 3. Maximum Force Check (Requires < 15%)
if pct_fwd < 15.0:
    print(f'[PASS] Maximum force on nose wheel | F_NW (Fwd CG) = {pct_fwd:.4f}% MTOW')
else:
    print(f'[FAIL] Maximum force on nose wheel | F_NW (Fwd CG) = {pct_fwd:.4f}% MTOW')

# 4. Static Tip Over Check
if x_cg_aft < x_MG:
    print(f'[PASS] Static tip over | delta = {x_MG - x_cg_aft:.2f} m')
else:
    print(f'[FAIL] Static tip over | delta = {x_MG - x_cg_aft:.2f} m')

# 4. Dynamyc Tip Over Check
if lamb < 55:
    print(f'[PASS] Dynamic tip over | lamb = {lamb:.2f} deg')
else:
    print(f'[FAIL] Dynamic tip over | delta = {lamb:.2f} deg')











