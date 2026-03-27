# ------------------------------------
# FLIGHT CHARACTERISTICS
# ------------------------------------
V = 250
altitude = 9000

# Operational limits
MTOW = 41640
MAX_FUEL = 8822
X_FUEL = 20.92
actual_MZFW = 33654

# Payload definitions
MASS_PAX = 87
MASS_FRONT_CARGO = 472
X_FRONT_CARGO = 7.77
MASS_AFT_CARGO = 1294
X_AFT_CARGO = 19.71

# Cabin rows (25 rows for 100 pax, 2+2 abreast)
NUM_ROWS = 25
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
y_centrenacelle = None
l_nac = 3.25
d_nac = None

# ------------------------------------
# COMPONENT WEIGHT FRACTIONS (% MTOW)
# ------------------------------------
MTOW = 45000

# ------------------------------------
# COMPONENT WEIGHT FRACTIONS (% EOW)
# ------------------------------------
EOW = 23188
WEIGHT_WINGp                = 19.7
WEIGHT_HORIZONTAL_TAILp     = 2.5
WEIGHT_VERTICAL_TAILp       = 1.8
WEIGHT_FUSELAGEp            = 35.0   # including cabin and furnishing systems
WEIGHT_MAIN_LANDING_GEARp   = 5.8
WEIGHT_NOSE_LANDING_GEARp   = 0.8
WEIGHT_PROPULSION_SYSTEMp   = 13.3   # including nacelles
WEIGHT_COCKPIT_SYSTEMSp     = 2.3    # avionics, furnishing, etc.