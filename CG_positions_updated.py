import numpy as np
import Input_updated as it

# =====================================================================
# CONSTANTS & PRE-CALCULATIONS (Independent of x_LEMACw)
# =====================================================================

# ------------------------------------
# BASIC INPUTS
# ------------------------------------
x_cockpit = it.x_cockpit
x_NW = it.x_NW
x_MG = it.x_MG
x_BAT = it.x_BAT
EOW = it.EOW

c_rw = it.c_rw
b_w = it.b_w
TAPER_RATIOw = it.TAPER_RATIOw
SWEEP_ANGLEw = it.SWEEP_ANGLEw

c_rh = it.c_rh
b_h = it.b_h
TAPER_RATIOh = it.TAPER_RATIOh
SWEEP_ANGLEh = it.SWEEP_ANGLEh
x_LEMACh = it.x_LEMACh

c_rv = it.c_rv
b_v = it.b_v
TAPER_RATIOv = it.TAPER_RATIOv
SWEEP_ANGLEv = it.SWEEP_ANGLEv
x_LEMACv = it.x_LEMACv
z_startvertical = it.z_startvertical

l_fus = it.l_fus
x_cgfusratio = it.x_cgfusratio
x_startnacelle = it.x_startnacelle
l_nac = it.l_nac

# ------------------------------------
# COMPONENT WEIGHTS
# ------------------------------------
WEIGHT_WING = it.WEIGHT_WING
WEIGHT_HORIZONTAL_TAIL = it.WEIGHT_HORIZONTAL_TAIL
WEIGHT_VERTICAL_TAIL = it.WEIGHT_VERTICAL_TAIL
WEIGHT_FUSELAGE = it.WEIGHT_FUSELAGE
WEIGHT_MAIN_LANDING_GEAR = it.WEIGHT_MAIN_LANDING_GEAR
WEIGHT_NOSE_LANDING_GEAR = it.WEIGHT_NOSE_LANDING_GEAR
WEIGHT_PROPULSION_SYSTEM = it.WEIGHT_PROPULSION_SYSTEM
WEIGHT_COCKPIT_SYSTEMS = it.WEIGHT_COCKPIT_SYSTEMS
WEIGHT_BATTERY = it.TOTAL_BATT_MASS

# Group Weights that remain constant
WEIGHT_fg = WEIGHT_FUSELAGE + WEIGHT_COCKPIT_SYSTEMS + WEIGHT_PROPULSION_SYSTEM + WEIGHT_HORIZONTAL_TAIL + WEIGHT_VERTICAL_TAIL + WEIGHT_NOSE_LANDING_GEAR + WEIGHT_BATTERY
WEIGHT_wg = WEIGHT_WING + WEIGHT_MAIN_LANDING_GEAR

# ------------------------------------
# CALCULATED DIMENSIONS
# ------------------------------------
c_macw = (2 / 3) * c_rw * (1 + TAPER_RATIOw + TAPER_RATIOw ** 2) / (1 + TAPER_RATIOw)
c_mach = (2 / 3) * c_rh * (1 + TAPER_RATIOh + TAPER_RATIOh ** 2) / (1 + TAPER_RATIOh)
c_macv = (2 / 3) * c_rv * (1 + TAPER_RATIOv + TAPER_RATIOv ** 2) / (1 + TAPER_RATIOv)

y_macw = (b_w / 6) * ((1 + 2 * TAPER_RATIOw) / (1 + TAPER_RATIOw))
y_mach = (b_h / 6) * ((1 + 2 * TAPER_RATIOh) / (1 + TAPER_RATIOh))
z_macv = (b_v / 3) * ((1 + 2 * TAPER_RATIOv) / (1 + TAPER_RATIOv))

# ------------------------------------
# FIXED CG (RELATIVE TO START OF OBJECT)
# ------------------------------------
y_cgw = 0.35 * b_w / 2
c_s = c_rw * (1 - (1 - TAPER_RATIOw) * 0.35)
distance_LEMAC_to_cs = (y_cgw - y_macw) * np.tan(np.radians(SWEEP_ANGLEw))
x_cgw_relative = 0.7 * c_s + distance_LEMAC_to_cs

x_cgh_relative = 0.42 * c_mach
y_cgh = 0.38 * b_h / 2

x_cgv_relative = 0.42 * c_macv
z_cgv_relative = 0.38 * b_v

x_cgn_relative = 0.4 * l_nac

# ------------------------------------
# CG OF STATIC COMPONENTS (FROM NOSE)
# ------------------------------------
x_cgh = x_LEMACh + x_cgh_relative
x_cgv = x_LEMACv + x_cgv_relative
x_cgfus = x_cgfusratio * l_fus
x_cgn = x_startnacelle + x_cgn_relative
x_cgbat = x_BAT

# ------------------------------------
# FUSELAGE GROUP CG (FROM NOSE)
# ------------------------------------
x_cgfg = (x_cgfus * WEIGHT_FUSELAGE +
          x_cockpit * WEIGHT_COCKPIT_SYSTEMS +
          x_cgn * WEIGHT_PROPULSION_SYSTEM +
          x_cgh * WEIGHT_HORIZONTAL_TAIL +
          x_cgv * WEIGHT_VERTICAL_TAIL +
          x_NW * WEIGHT_NOSE_LANDING_GEAR +
          x_cgbat * WEIGHT_BATTERY) / WEIGHT_fg


# =====================================================================
# DYNAMIC FUNCTION (Dependent on x_LEMACw)
# =====================================================================

def calculate_aircraft_cgs(x_LEMACw):
    """
    Calculates aircraft center of gravities based on wing placement.
    Requires global variables from the static pre-calculation block.
    """
    # ------------------------------------
    # DYNAMIC CG COMPUTATIONS (FROM NOSE)
    # ------------------------------------
    x_cgw = x_LEMACw + x_cgw_relative

    # Wing Group CG
    x_cgwg = (x_cgw * WEIGHT_WING + x_MG * WEIGHT_MAIN_LANDING_GEAR) / WEIGHT_wg

    # Aircraft Total CG
    x_cg = (x_cgfg * WEIGHT_fg + x_cgwg * WEIGHT_wg) / (WEIGHT_fg + WEIGHT_wg)

    # ------------------------------------
    # CG OF COMPONENTS (FROM LEMAC)
    # ------------------------------------
    x_cgw_LEMAC = x_cgw - x_LEMACw
    x_cgh_LEMAC = x_cgh - x_LEMACw
    x_cgv_LEMAC = x_cgv - x_LEMACw
    x_cgfus_LEMAC = x_cgfus - x_LEMACw
    x_cgn_LEMAC = x_cgn - x_LEMACw
    x_cgbat_LEMAC = x_cgbat - x_LEMACw

    x_cgfg_LEMAC = x_cgfg - x_LEMACw
    x_cgwg_LEMAC = x_cgwg - x_LEMACw
    x_cg_LEMAC = x_cg - x_LEMACw

    # ------------------------------------
    # CG OF COMPONENTS (NORMALISED BY WING MAC)
    # ------------------------------------
    x_cgw_LEMACNORM = x_cgw_LEMAC / c_macw
    x_cgh_LEMACNORM = x_cgh_LEMAC / c_macw
    x_cgv_LEMACNORM = x_cgv_LEMAC / c_macw
    x_cgfus_LEMACNORM = x_cgfus_LEMAC / c_macw
    x_cgn_LEMACNORM = x_cgn_LEMAC / c_macw
    x_cgbat_LEMACNORM = x_cgbat_LEMAC / c_macw

    x_cgfg_LEMACNORM = x_cgfg_LEMAC / c_macw
    x_cgwg_LEMACNORM = x_cgwg_LEMAC / c_macw
    x_cg_LEMACNORM = x_cg_LEMAC / c_macw

    # ------------------------------------
    # COMPILE RESULTS AND RETURN
    # ------------------------------------
    return {
        "from_nose": {
            "components": {
                "wing": x_cgw,
                "horizontal_stab": x_cgh,
                "vertical_stab": x_cgv,
                "fuselage": x_cgfus,
                "engine": x_cgn,
                "battery": x_cgbat
            },
            "groups": {
                "wing_group": x_cgwg,
                "fuselage_group": x_cgfg
            },
            "aircraft": x_cg
        },
        "from_lemac": {
            "components": {
                "wing": x_cgw_LEMAC,
                "horizontal_stab": x_cgh_LEMAC,
                "vertical_stab": x_cgv_LEMAC,
                "fuselage": x_cgfus_LEMAC,
                "engine": x_cgn_LEMAC,
                "battery": x_cgbat_LEMAC
            },
            "groups": {
                "wing_group": x_cgwg_LEMAC,
                "fuselage_group": x_cgfg_LEMAC
            },
            "aircraft": x_cg_LEMAC
        },
        "percent_mac": {
            "components": {
                "wing": x_cgw_LEMACNORM,
                "horizontal_stab": x_cgh_LEMACNORM,
                "vertical_stab": x_cgv_LEMACNORM,
                "fuselage": x_cgfus_LEMACNORM,
                "engine": x_cgn_LEMACNORM,
                "battery": x_cgbat_LEMACNORM
            },
            "groups": {
                "wing_group": x_cgwg_LEMACNORM,
                "fuselage_group": x_cgfg_LEMACNORM
            },
            "aircraft": x_cg_LEMACNORM
        }
    }


# =====================================================================
# EXECUTION / OUTPUTS
# =====================================================================
if __name__ == '__main__':
    # Fetch x_LEMACw from the inputs file as the variable to pass into our function
    x_LEMACw_input = it.x_LEMACw

    # Run the function
    results = calculate_aircraft_cgs(x_LEMACw_input)

    # Print the grouped results referencing the returned dictionary
    print("--- CG FROM NOSE ---")
    print(f"Wing Group: {results['from_nose']['groups']['wing_group']}")
    print(f"Fuselage Group: {results['from_nose']['groups']['fuselage_group']}")
    print(f"Total EOW Aircraft: {results['from_nose']['aircraft']}\n")

    print("--- CG FROM LEMAC ---")
    print(f"Wing Group: {results['from_lemac']['groups']['wing_group']}")
    print(f"Fuselage Group: {results['from_lemac']['groups']['fuselage_group']}")
    print(f"Total EOW Aircraft: {results['from_lemac']['aircraft']}\n")

    print("--- CG AS % MAC ---")
    wg_mac = results['percent_mac']['groups']['wing_group']
    fg_mac = results['percent_mac']['groups']['fuselage_group']
    ac_mac = results['percent_mac']['aircraft']

    print(f"Wing Group: {wg_mac:.4f} ({wg_mac * 100:.2f}%)")
    print(f"Fuselage Group: {fg_mac:.4f} ({fg_mac * 100:.2f}%)")
    print(f"Total EOW Aircraft: {ac_mac:.4f} ({ac_mac * 100:.2f}%)")