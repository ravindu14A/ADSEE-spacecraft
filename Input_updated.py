import Input as ip
# ------------------------------------
# FLIGHT CHARACTERISTICS
# ------------------------------------
M = 0.85
altitude = 9000
V_landing = 70
C_m0 = 0.01
CL_0 = 0.1

# Operational limits

X_FUEL = 20.92
actual_MZFW = 33654

# Payload definitions
MASS_PAX = 87
MASS_FRONT_CARGO = 472
X_START_FRONT_CARGOold = 6
X_END_FRONT_CARGOold = 9.55
MASS_AFT_CARGO = 1294
X_START_AFT_CARGOold = 18.90
X_END_AFT_CARGOold = 21.74

# Cabin rows (25 rows for 100 pax, 2+2 abreast)
NUM_ROWS = 22
X_ROW_1 = 6.0
ROW_PITCH = 0.7874
# ------------------------------------
# POSITIONS / DIMENSIONS
# ------------------------------------
z_cg = 4
#COCKPIT
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

# HORIZONTAL STABALISER DIMENSIONS
c_rh = 2.2
b_h = 8 # remember b for vertical stabaliser is simply its length
S_h = 15.91
TAPER_RATIOh = 0.35
SWEEP_ANGLEh = 30
x_LEMACh = 32

# VERTICAL STABALISER DIMENSIONS
c_rv = 4.2# Fixed duplicate c_rv
b_v = 4 # remember b for horizontal stabaliser is like wing
S_v = 11.32
TAPER_RATIOv = 0.7
SWEEP_ANGLEv = 35
x_LEMACv = 32
z_startvertical = 1.35

# Fuselage
l_fus = 39.13
d_fus = 4
x_cgfusratio = 0.45

# Engine
x_startnacelle = 30.0
y_centrenacelle = 3
l_nac = ip.l_nac *1.2
d_nac = ip.d_nac *1.2
n_nacelle = 2

# ------------------------------------
# COMPONENT WEIGHTS (Absolute Values in kg)
# ------------------------------------

# Operational Empty Weight (OEW)

W_pax_luggage = 8700
W_front_cargo = 472
W_aft_cargo = 1294
W_max_payload = W_pax_luggage + W_front_cargo + W_aft_cargo
MTOW = 41640

# ------------------------------------
# COMPONENT WEIGHT FRACTIONS (ABS)
# ------------------------------------
WEIGHT_WING                = 19.7 * ip.EOW *0.91
WEIGHT_HORIZONTAL_TAIL     = 2.5 * ip.EOW
WEIGHT_VERTICAL_TAIL       = 1.8* ip.EOW
WEIGHT_FUSELAGE            = 35.0* ip.EOW *0.93 # including cabin and furnishing systems
WEIGHT_MAIN_LANDING_GEAR   = 5.8* ip.EOW
WEIGHT_NOSE_LANDING_GEAR   = 0.8* ip.EOW
WEIGHT_PROPULSION_SYSTEM   = 13.3* ip.EOW   # including nacelles
WEIGHT_COCKPIT_SYSTEMS     = 2.3 * ip.EOW   # avionics, furnishing, etc.

WEIGHT_BATTERY_FWD = 2025
WEIGHT_BATTERY_AFT = 2475

VOLUME_BATTERY_FWD = 1300
VILUME_BATTERY_AFT = 1600

# ------------------------------------
# VOLUME AND LENGTH MATH
# ------------------------------------

TOTAL_CARGO_MASS = ip.MASS_FRONT_CARGO + ip.MASS_AFT_CARGO
V_total_orig = 19.4

V_front_orig = V_total_orig * (ip.MASS_FRONT_CARGO / TOTAL_CARGO_MASS) # ~5.18 m^3
V_aft_orig = V_total_orig * (ip.MASS_AFT_CARGO / TOTAL_CARGO_MASS)     # ~14.22 m^3

V_batt_front = 1.3 # m^3
V_batt_aft = 1.6   # m^3

# Original Hold Lengths
L_front_hold = X_END_FRONT_CARGOold - X_START_FRONT_CARGOold  # 3.55 m
L_aft_hold = X_END_AFT_CARGOold - X_START_AFT_CARGOold # 2.84 m

# Length occupied by batteries (assuming uniform cross-section)
L_batt_front = L_front_hold * (V_batt_front / V_front_orig) # ~0.89 m
L_batt_aft = L_aft_hold * (V_batt_aft / V_aft_orig)         # ~0.32 m

MASS_BATT_FRONT = 2025 # kg
MASS_BATT_AFT = 2475   # kg
TOTAL_BATT_MASS = MASS_BATT_FRONT + MASS_BATT_AFT

EOW =  WEIGHT_WING  + WEIGHT_HORIZONTAL_TAIL  +WEIGHT_VERTICAL_TAIL +WEIGHT_FUSELAGE  +WEIGHT_MAIN_LANDING_GEAR  +WEIGHT_NOSE_LANDING_GEAR   +WEIGHT_PROPULSION_SYSTEM  +WEIGHT_COCKPIT_SYSTEMS  +WEIGHT_BATTERY_FWD + WEIGHT_BATTERY_AFT+ TOTAL_BATT_MASS
EOW_BATT = EOW + TOTAL_BATT_MASS
W_fuel = MTOW - W_max_payload - EOW

# Batteries sit at the extremities of their respective holds
X_BATT_FRONT = X_START_FRONT_CARGOold+ (L_batt_front / 2)       # 6.445 m
X_BATT_AFT = X_END_AFT_CARGOold - (L_batt_aft / 2)          # 21.58 m


# 4. CARGO REDISTRIBUTION & EXACT CG LOCATIONS
# =====================================================================
V_front_new = V_front_orig - V_batt_front
V_aft_new = V_aft_orig - V_batt_aft
V_total_new = V_front_new + V_aft_new

MASS_FRONT_CARGO_EXX = TOTAL_CARGO_MASS * (V_front_new / V_total_new)
MASS_AFT_CARGO_EXX = TOTAL_CARGO_MASS * (V_aft_new / V_total_new)

# Remaining cargo space bounds
X_front_cargo_start = X_START_FRONT_CARGOold + L_batt_front
X_FRONT_CARGO = (X_front_cargo_start + X_END_FRONT_CARGOold) / 2 # 8.22 m

X_aft_cargo_end = X_END_AFT_CARGOold - L_batt_aft
X_AFT_CARGO = (X_START_AFT_CARGOold + X_aft_cargo_end) / 2       # 20.16 m

# ------------------------------------
# COMPONENT WEIGHT FRACTIONS (% MTOW)
# ------------------------------------
# Calculated as decimals (multiply by 100 for percentages)
frac_EOW = EOW / MTOW
frac_max_payload = W_max_payload / MTOW
frac_pax_luggage = W_pax_luggage / MTOW
frac_front_cargo = W_front_cargo / MTOW
frac_aft_cargo = W_aft_cargo / MTOW
frac_fuel = W_fuel / MTOW

TOTAL_PAX_WEIGHT = NUM_ROWS * 4 * 87

MZFW_EXX = EOW_BATT + TOTAL_PAX_WEIGHT + TOTAL_CARGO_MASS
MAX_ALLOWABLE_FUEL_EXX = MTOW - MZFW_EXX