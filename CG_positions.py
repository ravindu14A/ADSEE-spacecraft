import numpy as np
import Input as it

# ------------------------------------
# INPUT
# ------------------------------------
#COCKPIT
x_cockpit = it.x_cockpit

# WHEELS
x_NW = it.x_NW
x_MG = it.x_MG

#WEIGHTS
EOW = it.EOW

# WING DIMENSION
c_rw = it.c_rw
b_w = it.b_w
TAPER_RATIOw = it.TAPER_RATIOw
SWEEP_ANGLEw = it.SWEEP_ANGLEw # Assume degrees, leading edge sweep
x_LEMACw = it.x_LEMACw


# HORIZONTAL STABALISER DIMENSIONS
c_rh = it.c_rh
b_h = it.b_h # remember b for vertical stabaliser is simply its length
TAPER_RATIOh = it.TAPER_RATIOh
SWEEP_ANGLEh = it.SWEEP_ANGLEh
x_LEMACh = it.x_LEMACh


# VERTICAL STABALISER DIMENSIONS
c_rv = it.c_rv
b_v = it.b_v # remember b for horizontal stabaliser is like wing
TAPER_RATIOv = it.TAPER_RATIOv
SWEEP_ANGLEv = it.SWEEP_ANGLEv
x_LEMACv = it.x_LEMACv
z_startvertical = it.z_startvertical


# Fuselage and Engine
length_fus = it.length_fus
x_cgfusratio = it.x_cgfusratio

x_startnacelle = it.x_startnacelle
length_nac = it.length_nac

# ------------------------------------
# COMPONENT WEIGHT
# ------------------------------------
WEIGHT_WING                = it.WEIGHT_WINGp / 100 * EOW
WEIGHT_HORIZONTAL_TAIL     = it.WEIGHT_HORIZONTAL_TAILp / 100 * EOW
WEIGHT_VERTICAL_TAIL       = it.WEIGHT_VERTICAL_TAILp / 100 * EOW
WEIGHT_FUSELAGE            = it.WEIGHT_FUSELAGEp / 100 * EOW
WEIGHT_MAIN_LANDING_GEAR   = it.WEIGHT_MAIN_LANDING_GEARp / 100 * EOW
WEIGHT_NOSE_LANDING_GEAR   = it.WEIGHT_NOSE_LANDING_GEARp / 100 * EOW
WEIGHT_PROPULSION_SYSTEM   = it.WEIGHT_PROPULSION_SYSTEMp / 100 * EOW
WEIGHT_COCKPIT_SYSTEMS     = it.WEIGHT_COCKPIT_SYSTEMSp / 100 * EOW

# ------------------------------------
# CALCULATED DIMENSIONS
# ------------------------------------ names
c_macw = (2 / 3) * c_rw * (1 + TAPER_RATIOw + TAPER_RATIOw**2) / (1 + TAPER_RATIOw)
c_mach = (2 / 3) * c_rh * (1 + TAPER_RATIOh + TAPER_RATIOh**2) / (1 + TAPER_RATIOh)
c_macv = (2 / 3) * c_rv * (1 + TAPER_RATIOv + TAPER_RATIOv**2) / (1 + TAPER_RATIOv)

y_macw = (b_w / 6) * ((1 + 2 * TAPER_RATIOw) / (1 + TAPER_RATIOw))
y_mach = (b_h / 6) * ((1 + 2 * TAPER_RATIOh) / (1 + TAPER_RATIOh))
z_macv = (b_v / 3) * ((1 + 2 * TAPER_RATIOv) / (1 + TAPER_RATIOv))

# ------------------------------------
# FIXED CG (FROM START OF OBJECT - LEMAC FOR LIFT CREATING SURFACES)
# ------------------------------------
# WING
y_cgw = 0.35 * b_w / 2

c_s = c_rw * (1 - (1 - TAPER_RATIOw) * 0.35)
distance_LEMAC_to_cs = (y_cgw - y_macw) * np.tan(np.radians(SWEEP_ANGLEw))
x_cgw_relative = 0.7 * c_s + distance_LEMAC_to_cs

#HORIZONTAL STABALISER
x_cgh_relative = 0.42 * c_mach
y_cgh = 0.38 * b_h / 2

#VERTICAL STABALISER
x_cgv_relative = 0.42 * c_macv
z_cgv_relative = 0.38 * b_v

#ENGINES
x_cgn_relative = 0.4 * length_nac


# ------------------------------------
# FIXED CG (FROM NOSE)
# ------------------------------------
# WING
x_cgw = x_LEMACw + x_cgw_relative

# HORIZONTAL STABALISER
x_cgh = x_LEMACh + x_cgh_relative

# VERTICAL STABALISER
x_cgv = x_LEMACv + x_cgv_relative

# FUSELAGE
x_cgfus = x_cgfusratio * length_fus

# ENGINE
x_cgn = x_startnacelle + x_cgn_relative

# ------------------------------------
# FUSELAGE GROUP CG
# ------------------------------------
WEIGHT_fg = WEIGHT_FUSELAGE + WEIGHT_COCKPIT_SYSTEMS + WEIGHT_PROPULSION_SYSTEM + WEIGHT_HORIZONTAL_TAIL + WEIGHT_VERTICAL_TAIL + WEIGHT_NOSE_LANDING_GEAR
x_cgfg = (x_cgfus * WEIGHT_FUSELAGE + x_cockpit * WEIGHT_COCKPIT_SYSTEMS + x_cgn * WEIGHT_PROPULSION_SYSTEM + x_cgh * WEIGHT_HORIZONTAL_TAIL + x_cgv * WEIGHT_VERTICAL_TAIL + x_NW * WEIGHT_NOSE_LANDING_GEAR) / WEIGHT_fg

# ------------------------------------
# WING GROUP CG
# ------------------------------------
WEIGHT_wg = WEIGHT_WING + WEIGHT_MAIN_LANDING_GEAR
x_cgwg = (x_cgw * WEIGHT_WING + x_MG * WEIGHT_MAIN_LANDING_GEAR) / WEIGHT_wg

x_cg = (x_cgfg * WEIGHT_fg + x_cgwg * WEIGHT_wg) / (WEIGHT_fg + WEIGHT_wg)

print(f'Center of Gravity position of Wing Group: {x_cgwg}')
print(f'Center of Gravity position of Fuselage Group: {x_cgfg}')
print(f'Center of Gravity position of EOW Aircraft: {x_cg}')