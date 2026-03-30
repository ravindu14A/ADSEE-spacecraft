import Input as ip

# ------------------------------------
# FLIGHT CHARACTERISTICS
# ------------------------------------
M = ip.M
altitude = ip.altitude
CL_max = 2.6
C_m0 = ip.C_m0
CL_0 = ip.CL_0

# ------------------------------------
# PAYLOAD DEFINITIONS & CABIN
# ------------------------------------
MASS_PAX = 87

# Old cargo definitions for volume calculation
MASS_FRONT_CARGOold = 472
MASS_AFT_CARGOold = 1294

X_START_FRONT_CARGOold = 7.1
X_END_FRONT_CARGOold = 9.55
X_START_AFT_CARGOold = 25.2
X_END_AFT_CARGOold = 27.84

# Cabin rows (Point VI: 25 - 3 = 22 rows)
NUM_ROWS = 22
X_ROW_1 = 6.0
ROW_PITCH = 0.7874

# ------------------------------------
# POSITIONS / DIMENSIONS
# ------------------------------------
# Point XI: Landing gear height increased by 30cm (0.3m)
z_cg = ip.z_cg + 0.3
x_cockpit = ip.x_cockpit

# WHEELS
x_NW = ip.x_NW
x_MG = ip.x_MG
y_MG = ip.y_MG
number_MG = ip.number_MG
theta = ip.theta


# WING DIMENSION
c_rw = ip.c_rw
b_w = ip.b_w
S_w = ip.S_w
TAPER_RATIOw = ip.TAPER_RATIOw
SWEEP_ANGLEw = ip.SWEEP_ANGLEw
x_LEMACw = ip.x_LEMACw -0.82
dihedral = ip.dihedral
front_spar_fraction = ip.front_spar_fraction
rear_spar_fraction = ip.rear_spar_fraction

# HORIZONTAL STABILISER DIMENSIONS
c_rh = ip.c_rh
c_th = ip.c_th
S_h = ip.S_h -0.53
b_h = 2 * S_h / (c_rh + c_th)
TAPER_RATIOh = ip.TAPER_RATIOh
SWEEP_ANGLEh = ip.SWEEP_ANGLEh
x_LEMACh = ip.x_LEMACh

# VERTICAL STABILISER DIMENSIONS
c_rv = ip.c_rv
c_tv = ip.c_tv
S_v = ip.S_v
b_v = 2 * S_v / (c_rv + c_tv)
TAPER_RATIOv = ip.TAPER_RATIOv
SWEEP_ANGLEv = ip.SWEEP_ANGLEv
x_LEMACv = ip.x_LEMACv
z_startvertical = ip.z_startvertical

# Fuselage
l_fus = ip.l_fus
d_fus = ip.d_fus
x_cgfusratio = ip.x_cgfusratio

# Engine (Point I: +20% length and diameter)
# (Location x_startnacelle pulls from original to ensure CG stays locked)
x_startnacelle = ip.x_startnacelle
y_centrenacelle = ip.y_centrenacelle
l_nac = ip.l_nac * 1.2
d_nac = ip.d_nac * 1.2
n_nacelle = ip.n_nacelle

# ------------------------------------
# VOLUME AND LENGTH MATH (Point IV & VII)
# ------------------------------------
TOTAL_CARGO_MASS = MASS_FRONT_CARGOold + MASS_AFT_CARGOold
V_total_orig = 19.4

V_front_orig = V_total_orig * (MASS_FRONT_CARGOold / TOTAL_CARGO_MASS)
V_aft_orig = V_total_orig * (MASS_AFT_CARGOold / TOTAL_CARGO_MASS)

V_batt_front = 1.3
V_batt_aft = 1.6

# Original Hold Lengths
L_front_hold = X_END_FRONT_CARGOold - X_START_FRONT_CARGOold
L_aft_hold = X_END_AFT_CARGOold - X_START_AFT_CARGOold

# Length occupied by batteries
L_batt_front = L_front_hold * (V_batt_front / V_front_orig)
L_batt_aft = L_aft_hold * (V_batt_aft / V_aft_orig)

# Battery Weights (Left as individual stated values)
MASS_BATT_FRONT = 2025
MASS_BATT_AFT = 2475
TOTAL_BATT_MASS = MASS_BATT_FRONT + MASS_BATT_AFT

# Batteries sit at the extremities of their respective holds (Point IV)
X_BATT_FRONT = X_START_FRONT_CARGOold + (L_batt_front / 2)
X_BATT_AFT = X_END_AFT_CARGOold - (L_batt_aft / 2)

# CARGO REDISTRIBUTION & EXACT CG LOCATIONS (Point VII)
V_front_new = V_front_orig - V_batt_front
V_aft_new = V_aft_orig - V_batt_aft
V_total_new = V_front_new + V_aft_new

MASS_FRONT_CARGO_EXX = TOTAL_CARGO_MASS * (V_front_new / V_total_new)
MASS_AFT_CARGO_EXX = TOTAL_CARGO_MASS * (V_aft_new / V_total_new)

# Reassign primary cargo variables so they export correctly
MASS_FRONT_CARGO = MASS_FRONT_CARGO_EXX
MASS_AFT_CARGO = MASS_AFT_CARGO_EXX

# Remaining cargo space bounds
X_front_cargo_start = X_START_FRONT_CARGOold + L_batt_front
X_FRONT_CARGO = (X_front_cargo_start + X_END_FRONT_CARGOold) / 2

X_aft_cargo_end = X_END_AFT_CARGOold - L_batt_aft
X_AFT_CARGO = (X_START_AFT_CARGOold + X_aft_cargo_end) / 2

# ------------------------------------
# COMPONENT WEIGHTS (Point III)
# ------------------------------------
WEIGHT_WING                = (19.7/100) * ip.EOW * 0.91
WEIGHT_HORIZONTAL_TAIL     = (2.5/100) * ip.EOW
WEIGHT_VERTICAL_TAIL       = (1.8/100) * ip.EOW
WEIGHT_FUSELAGE            = (35.0/100) * ip.EOW * 0.93
WEIGHT_MAIN_LANDING_GEAR   = (5.8/100) * ip.EOW
WEIGHT_NOSE_LANDING_GEAR   = (0.8/100) * ip.EOW
WEIGHT_PROPULSION_SYSTEM   = (13.3/100) * ip.EOW
WEIGHT_COCKPIT_SYSTEMS     = (2.3/100) * ip.EOW

# Calculate the exact missing mass (18.8%) from the original EOW
WEIGHT_UNACCOUNTED         = (18.8/100) * ip.EOW

# Point V: Batteries are not removable, EOW includes them.
EOW = (WEIGHT_WING + WEIGHT_HORIZONTAL_TAIL + WEIGHT_VERTICAL_TAIL +
       WEIGHT_FUSELAGE + WEIGHT_MAIN_LANDING_GEAR + WEIGHT_NOSE_LANDING_GEAR +
       WEIGHT_PROPULSION_SYSTEM + WEIGHT_COCKPIT_SYSTEMS + WEIGHT_UNACCOUNTED + TOTAL_BATT_MASS)

# ------------------------------------
# AIRCRAFT MTOW & FUEL (Point VIII)
# ------------------------------------
MTOW = 41640 # Remains identical to CRJ-1000

W_pax_luggage = NUM_ROWS * 4 * MASS_PAX
W_front_cargo = MASS_FRONT_CARGO
W_aft_cargo = MASS_AFT_CARGO

W_max_payload = W_pax_luggage + W_front_cargo + W_aft_cargo

# Fuel mathematically compensates for payload and EOW shifts
W_fuel = MTOW - W_max_payload - EOW

MZFW_EXX = EOW + W_max_payload
MAX_ALLOWABLE_FUEL_EXX = MTOW - MZFW_EXX

if __name__ == '__main__':
    print(f"Calculated MZFW: {MZFW_EXX:.2f} kg")
    print(f"Calculated Fuel: {W_fuel:.2f} kg")
    print(f"New EOW (Including Batteries): {EOW:.2f} kg")
    print(f"Updated Z-CG: {z_cg:.2f} m")