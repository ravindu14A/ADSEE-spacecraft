import Input as ip

# ------------------------------------
# FLIGHT CHARACTERISTICS
# ------------------------------------
M = 0.85
altitude = 9000
V_landing = 70
C_m0 = 0.01
CL_0 = 0.1

# ------------------------------------
# PAYLOAD DEFINITIONS & CABIN
# ------------------------------------
MASS_PAX = 87

# Old cargo definitions for volume calculation
MASS_FRONT_CARGOold = 472
MASS_AFT_CARGOold = 1294

X_START_FRONT_CARGOold = 6
X_END_FRONT_CARGOold = 9.55
X_START_AFT_CARGOold = 18.90
X_END_AFT_CARGOold = 21.74

# Cabin rows (Point VI: 25 - 3 = 22 rows)
NUM_ROWS = 22
X_ROW_1 = 6.0
ROW_PITCH = 0.7874

# ------------------------------------
# POSITIONS / DIMENSIONS
# ------------------------------------
z_cg = 4
x_cockpit = 2.5

# WHEELS
x_NW = 3.0
x_MG = 22.6
y_MG = 4
number_MG = 2
theta = 12
X_FUEL = 20.92

# WING DIMENSION
c_rw = 4.5
b_w = 26.18
S_w = 77.4
TAPER_RATIOw = 0.3
SWEEP_ANGLEw = 30
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

# Fuselage
l_fus = 39.13
d_fus = 4
x_cgfusratio = 0.45

# Engine (Point I: +20% length and diameter)
x_startnacelle = 30.0
y_centrenacelle = 3
l_nac = ip.l_nac * 1.2
d_nac = ip.d_nac * 1.2
n_nacelle = 2

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
# Total aircraft mass now equals exactly 100% of components + Batteries
EOW = (WEIGHT_WING + WEIGHT_HORIZONTAL_TAIL + WEIGHT_VERTICAL_TAIL +
       WEIGHT_FUSELAGE + WEIGHT_MAIN_LANDING_GEAR + WEIGHT_NOSE_LANDING_GEAR +
       WEIGHT_PROPULSION_SYSTEM + WEIGHT_COCKPIT_SYSTEMS + WEIGHT_UNACCOUNTED + TOTAL_BATT_MASS)

# ------------------------------------
# AIRCRAFT MTOW & FUEL (Point VIII)
# ------------------------------------
MTOW = 41640 # Remains identical to CRJ-1000 per prompt

W_pax_luggage = NUM_ROWS * 4 * MASS_PAX
W_front_cargo = MASS_FRONT_CARGO
W_aft_cargo = MASS_AFT_CARGO

W_max_payload = W_pax_luggage + W_front_cargo + W_aft_cargo

# Fuel mathematically compensates for payload and EOW shifts
W_fuel = MTOW - W_max_payload - EOW

MZFW_EXX = EOW + W_max_payload
MAX_ALLOWABLE_FUEL_EXX = MTOW - MZFW_EXX

# ------------------------------------
# COMPONENT WEIGHT FRACTIONS (% MTOW)
# ------------------------------------
frac_EOW = EOW / MTOW
frac_max_payload = W_max_payload / MTOW
frac_pax_luggage = W_pax_luggage / MTOW
frac_front_cargo = W_front_cargo / MTOW
frac_aft_cargo = W_aft_cargo / MTOW
frac_fuel = W_fuel / MTOW

if __name__ == '__main__':
    print(f"Calculated MZFW: {MZFW_EXX:.2f} kg")
    print(f"Calculated Fuel: {W_fuel:.2f} kg")
    print(EOW)
