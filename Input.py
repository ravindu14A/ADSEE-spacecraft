# ------------------------------------
# FLIGHT CHARACTERISTICS
# ------------------------------------
M = 0.82
altitude = 9000
V_landing = 70
C_m0 = 0.01
CL_0 = 0.1

# Operational limits

actual_MZFW = 33654

# Payload definitions
MASS_PAX = 87
MASS_FRONT_CARGO = 472
X_FRONT_CARGO = 8.33
MASS_AFT_CARGO = 1294
X_AFT_CARGO = 26.52

# Cabin rows (25 rows for 100 pax, 2+2 abreast)
NUM_ROWS = 25
X_ROW_1 = 7.1
ROW_PITCH = 0.7874
# ------------------------------------
# POSITIONS / DIMENSIONS
# ------------------------------------
# Fuselage
l_fus = 39.13
d_fus = 4
x_cgfusratio = 0.45


#COCKPIT
x_cockpit = 2.5
z_cg = 4

# WHEELS
x_NW = 3.0
x_MG = 22.64 #258/446
y_MG = 2.0375
number_MG = 2
theta = 15

# WING DIMENSION
c_rw = 5.12
b_w = 26.2
S_w = 77.4
TAPER_RATIOw = 0.3
SWEEP_ANGLEw = 29.5 # Degrees, leading edge sweep
x_LEMACw = 20.5 # 296/566
dihedral = None
front_spar_fraction = 0.2
rear_spar_fraction = 0.8

# HORIZONTAL STABALISER DIMENSIONS
c_rh = 2.8 # 40/566
c_th = 1.2 # 17/566
b_h = 9 # 130/55
S_h = 15.91
TAPER_RATIOh = c_th / c_rh
SWEEP_ANGLEh = 33.7
x_LEMACh = 38.9 #563/566

# VERTICAL STABALISER DIMENSIONS
c_rv = 3.5# 40/446
c_tv = 2.8# 27/446
b_v = 4 # remember b for horizontal stabaliser is like wing
S_v = 11.32
TAPER_RATIOv = c_tv / c_rv
SWEEP_ANGLEv = 42.6
x_LEMACv = 35
z_startvertical = 1.35

# Engine
x_startnacelle = 30
y_centrenacelle = 3
l_nac = 3.25
d_nac = 1
n_nacelle = 2


# ------------------------------------
# COMPONENT WEIGHTS (Absolute Values in kg)
# ------------------------------------

# Operational Empty Weight (OEW)
EOW = 23188
W_pax_luggage = 8700
W_front_cargo = 472
W_aft_cargo = 1294
W_max_payload = W_pax_luggage + W_front_cargo + W_aft_cargo
MTOW = 41640
W_fuel = MTOW - W_max_payload - EOW

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

# ------------------------------------
# COMPONENT WEIGHT FRACTIONS (% EOW)
# ------------------------------------
WEIGHT_WINGp                = 19.7
WEIGHT_HORIZONTAL_TAILp     = 2.5
WEIGHT_VERTICAL_TAILp       = 1.8
WEIGHT_FUSELAGEp            = 35.0   # including cabin and furnishing systems
WEIGHT_MAIN_LANDING_GEARp   = 5.8
WEIGHT_NOSE_LANDING_GEARp   = 0.8
WEIGHT_PROPULSION_SYSTEMp   = 13.3   # including nacelles
WEIGHT_COCKPIT_SYSTEMSp     = 2.3    # avionics, furnishing, etc.
