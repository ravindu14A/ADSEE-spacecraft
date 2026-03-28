# =====================================================================
# CRJ-EXX UPDATED INPUT FILE (Task 3.3a)
# =====================================================================
import Input as ip
# ------------------------------------
# FLIGHT CHARACTERISTICS
# ------------------------------------
V = 250
altitude = 9000

# Operational limits
MTOW = 41640
MAX_FUEL_CAPACITY = 8822  # Structural tank capacity (kg)
X_FUEL = 20.92

# ------------------------------------
# POSITIONS / DIMENSIONS (UNMODIFIED)
# ------------------------------------
# COCKPIT
x_cockpit = 2.5

# WHEELS
x_NW = 3.0
x_MG = 22.6
y_MG = 4
number_MG = 2
theta = 12

# WING DIMENSION
c_rw = 4.5
b_w = 26.18
S_w = 77.4
TAPER_RATIOw = 0.3
SWEEP_ANGLEw = 30 # Degrees, leading edge sweep
x_LEMACw = 19
dihedral = None

# HORIZONTAL STABILISER DIMENSIONS
c_rh = 2.2
b_h = 8
S_h = 15.91
TAPER_RATIOh = 0.35
SWEEP_ANGLEh = 30
x_LEMACh = 32

# VERTICAL STABILISER DIMENSIONS
c_rv = 4.2
b_v = 4
S_v = 11.32
TAPER_RATIOv = 0.7
SWEEP_ANGLEv = 35
x_LEMACv = 32
z_startvertical = 1.35

# FUSELAGE
l_fus = 39.13
d_fus = 4
x_cgfusratio = 0.45

# ------------------------------------
# MODIFIED GEOMETRY (CRJ-EXX Updates)
# ------------------------------------
# Landing gear height increased by 30cm (+0.3m)
z_cg = 4.0 + 0.3  # Now 4.3 m

# Engine / Nacelle (Length increased by 20%, but CG is unchanged)
x_startnacelle = 30.0
y_centrenacelle = None
l_nac_original = ip.l_nac
d_nac_original = ip.d_nac
l_nac = ip.l_nac * 1.20  # Now 3.90 m
d_nac = ip.d_nac * 1.20

# ------------------------------------
# EMPTY WEIGHT (EOW) REDUCTIONS
# ------------------------------------
EOW_orig = 23188
W_wing_orig = (19.7 / 100) * EOW_orig
W_fuselage_orig = (35.0 / 100) * EOW_orig

# Reduced by 9% (Wing) and 7% (Fuselage)
W_wing_EXX = W_wing_orig * (1 - 0.09)
W_fuselage_EXX = W_fuselage_orig * (1 - 0.07)

delta_wing = W_wing_orig - W_wing_EXX
delta_fuselage = W_fuselage_orig - W_fuselage_EXX
total_weight_savings = delta_wing + delta_fuselage

# New baseline EOW (without batteries)
EOW = EOW_orig - total_weight_savings
x_BATaft = 20
x_BATfwd = 20
# ------------------------------------
# ABSOLUTE COMPONENT WEIGHTS (CRJ-EXX)
# ------------------------------------
# We use absolute weights (kg) instead of percentages now to prevent math drift
WEIGHT_WING                = W_wing_EXX
WEIGHT_HORIZONTAL_TAIL     = (2.5 / 100) * EOW_orig
WEIGHT_VERTICAL_TAIL       = (1.8 / 100) * EOW_orig
WEIGHT_FUSELAGE            = W_fuselage_EXX
WEIGHT_MAIN_LANDING_GEAR   = (5.8 / 100) * EOW_orig
WEIGHT_NOSE_LANDING_GEAR   = (0.8 / 100) * EOW_orig
WEIGHT_PROPULSION_SYSTEM   = (13.3 / 100) * EOW_orig
WEIGHT_COCKPIT_SYSTEMS     = (2.3 / 100) * EOW_orig

# ------------------------------------
# BATTERIES (4500 kg Total Assumption)
# ------------------------------------
MASS_BATT_FRONT = 2025 # kg
MASS_BATT_AFT = 2475   # kg
TOTAL_BATT_MASS = MASS_BATT_FRONT + MASS_BATT_AFT

# Battery Volumes & Lengths (Based on actual cargo boundaries)
V_batt_front = 1.3 # m^3
V_batt_aft = 1.6   # m^3
L_front_hold = 9.55 - 6.00  # 3.55 m
L_aft_hold = 21.74 - 18.90  # 2.84 m

# Battery exact CGs (Occupying the extreme forward and aft spaces)
L_batt_front = L_front_hold * (V_batt_front / 5.18) # ~0.89 m
L_batt_aft = L_aft_hold * (V_batt_aft / 14.22)      # ~0.32 m

X_BATT_FRONT = 6.00 + (L_batt_front / 2)       # 6.445 m
X_BATT_AFT = 21.74 - (L_batt_aft / 2)          # 21.580 m

# ------------------------------------
# PAYLOAD: PASSENGERS & CARGO (CRJ-EXX)
# ------------------------------------
# Passengers (Last 3 rows removed: 25 -> 22)
NUM_ROWS = 22
MASS_PAX = 87
X_ROW_1 = 6.0
ROW_PITCH = 0.7874

# Cargo (Redistributed based on remaining volume)
TOTAL_CARGO_MASS = 472 + 1294 # 1766 kg

V_front_new = 5.18 - V_batt_front # 3.88 m^3
V_aft_new = 14.22 - V_batt_aft    # 12.62 m^3
V_total_new = V_front_new + V_aft_new

MASS_FRONT_CARGO = TOTAL_CARGO_MASS * (V_front_new / V_total_new) # 415.8 kg
MASS_AFT_CARGO = TOTAL_CARGO_MASS * (V_aft_new / V_total_new)     # 1350.2 kg

# New Cargo CGs (Shifted due to battery displacement)
X_FRONT_CARGO = ((6.00 + L_batt_front) + 9.55) / 2 # 8.22 m
X_AFT_CARGO = (18.90 + (21.74 - L_batt_aft)) / 2   # 20.16 m

# ------------------------------------
# WEIGHT ENVELOPE (CRJ-EXX)
# ------------------------------------
TOTAL_PAX_WEIGHT = NUM_ROWS * 4 * MASS_PAX
EOW_BATT = EOW + TOTAL_BATT_MASS

# Recalculated MZFW
actual_MZFW = EOW_BATT + TOTAL_PAX_WEIGHT + TOTAL_CARGO_MASS

# Max Allowable Fuel Drop (To respect fixed MTOW)
MAX_FUEL = MTOW - actual_MZFW