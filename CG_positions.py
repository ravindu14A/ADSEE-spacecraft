import numpy as np
import Input as it


def calculate_aircraft_cg(x_LEMACw):
    # ------------------------------------
    # COMPONENT WEIGHTS
    # ------------------------------------
    WEIGHT_WING = it.WEIGHT_WINGp / 100 * it.EOW
    WEIGHT_HORIZONTAL_TAIL = it.WEIGHT_HORIZONTAL_TAILp / 100 * it.EOW
    WEIGHT_VERTICAL_TAIL = it.WEIGHT_VERTICAL_TAILp / 100 * it.EOW
    WEIGHT_FUSELAGE = it.WEIGHT_FUSELAGEp / 100 * it.EOW
    WEIGHT_MAIN_LANDING_GEAR = it.WEIGHT_MAIN_LANDING_GEARp / 100 * it.EOW
    WEIGHT_NOSE_LANDING_GEAR = it.WEIGHT_NOSE_LANDING_GEARp / 100 * it.EOW
    WEIGHT_PROPULSION_SYSTEM = it.WEIGHT_PROPULSION_SYSTEMp / 100 * it.EOW
    WEIGHT_COCKPIT_SYSTEMS = it.WEIGHT_COCKPIT_SYSTEMSp / 100 * it.EOW

    # ------------------------------------
    # CALCULATED DIMENSIONS
    # ------------------------------------
    c_macw = (2 / 3) * it.c_rw * (1 + it.TAPER_RATIOw + it.TAPER_RATIOw ** 2) / (1 + it.TAPER_RATIOw)
    c_mach = (2 / 3) * it.c_rh * (1 + it.TAPER_RATIOh + it.TAPER_RATIOh ** 2) / (1 + it.TAPER_RATIOh)
    c_macv = (2 / 3) * it.c_rv * (1 + it.TAPER_RATIOv + it.TAPER_RATIOv ** 2) / (1 + it.TAPER_RATIOv)

    y_macw = (it.b_w / 6) * ((1 + 2 * it.TAPER_RATIOw) / (1 + it.TAPER_RATIOw))
    y_mach = (it.b_h / 6) * ((1 + 2 * it.TAPER_RATIOh) / (1 + it.TAPER_RATIOh))
    z_macv = (it.b_v / 3) * ((1 + 2 * it.TAPER_RATIOv) / (1 + it.TAPER_RATIOv))

    # ------------------------------------
    # FIXED CG (RELATIVE TO COMPONENT DATUM)
    # ------------------------------------
    # WING
    y_cgw = 0.35 * it.b_w / 2
    c_s = it.c_rw * (1 - (1 - it.TAPER_RATIOw) * 0.35)
    distance_LEMAC_to_cs = (y_cgw - y_macw) * np.tan(np.radians(it.SWEEP_ANGLEw))
    x_cgw_relative = 0.7 * c_s + distance_LEMAC_to_cs

    # HORIZONTAL STABILISER
    x_cgh_relative = 0.42 * c_mach

    # VERTICAL STABILISER
    x_cgv_relative = 0.42 * c_macv

    # ENGINES
    x_cgn_relative = 0.4 * it.l_nac

    # ------------------------------------
    # CG OF COMPONENTS (FROM NOSE)
    # ------------------------------------
    x_cgw = x_LEMACw + x_cgw_relative
    x_cgh = it.x_LEMACh + x_cgh_relative
    x_cgv = it.x_LEMACv + x_cgv_relative
    x_cgfus = it.x_cgfusratio * it.l_fus
    x_cgn = it.x_startnacelle + x_cgn_relative

    # ------------------------------------
    # FUSELAGE GROUP CG (FROM NOSE)
    # ------------------------------------
    WEIGHT_fg = (WEIGHT_FUSELAGE + WEIGHT_COCKPIT_SYSTEMS + WEIGHT_PROPULSION_SYSTEM +
                 WEIGHT_HORIZONTAL_TAIL + WEIGHT_VERTICAL_TAIL + WEIGHT_NOSE_LANDING_GEAR)

    x_cgfg = (x_cgfus * WEIGHT_FUSELAGE + it.x_cockpit * WEIGHT_COCKPIT_SYSTEMS +
              x_cgn * WEIGHT_PROPULSION_SYSTEM + x_cgh * WEIGHT_HORIZONTAL_TAIL +
              x_cgv * WEIGHT_VERTICAL_TAIL + it.x_NW * WEIGHT_NOSE_LANDING_GEAR) / WEIGHT_fg

    # ------------------------------------
    # WING GROUP CG (FROM NOSE)
    # ------------------------------------
    WEIGHT_wg = WEIGHT_WING + WEIGHT_MAIN_LANDING_GEAR
    x_cgwg = (x_cgw * WEIGHT_WING + it.x_MG * WEIGHT_MAIN_LANDING_GEAR) / WEIGHT_wg

    # ------------------------------------
    # AIRCRAFT CG (FROM NOSE)
    # ------------------------------------
    x_cg = (x_cgfg * WEIGHT_fg + x_cgwg * WEIGHT_wg) / (WEIGHT_fg + WEIGHT_wg)

    # ------------------------------------
    # CG NORMALISED BY MAC (FROM LEMAC)
    # ------------------------------------
    x_cgwg_LEMACNORM = (x_cgwg - x_LEMACw) / c_macw
    x_cgfg_LEMACNORM = (x_cgfg - x_LEMACw) / c_macw
    x_cg_LEMACNORM = (x_cg - x_LEMACw) / c_macw

    return {
        "x_cgwg": x_cgwg,
        "x_cgfg": x_cgfg,
        "x_cg": x_cg,
        "x_cgwg_LEMAC": x_cgwg - x_LEMACw,
        "x_cgfg_LEMAC": x_cgfg - x_LEMACw,
        "x_cg_LEMAC": x_cg - x_LEMACw,
        "x_cgwg_LEMACNORM": x_cgwg_LEMACNORM,
        "x_cgfg_LEMACNORM": x_cgfg_LEMACNORM,
        "x_cg_LEMACNORM": x_cg_LEMACNORM
    }


# ------------------------------------
# MAIN RUN
# ------------------------------------
if __name__ == '__main__':
    # Call function using the variable from Input.py
    results = calculate_aircraft_cg(it.x_LEMACw)

    print("--- CG FROM NOSE ---")
    print(f"Wing Group: {results['x_cgwg']:.4f}")
    print(f"Fuselage Group: {results['x_cgfg']:.4f}")
    print(f"Total EOW Aircraft: {results['x_cg']:.4f}\n")

    print("--- CG FROM LEMAC ---")
    print(f"Wing Group: {results['x_cgwg_LEMAC']:.4f}")
    print(f"Fuselage Group: {results['x_cgfg_LEMAC']:.4f}")
    print(f"Total EOW Aircraft: {results['x_cg_LEMAC']:.4f}\n")

    print("--- CG AS % MAC ---")
    print(f"Wing Group: {results['x_cgwg_LEMACNORM']:.4f} ({results['x_cgwg_LEMACNORM'] * 100:.2f}%)")
    print(f"Fuselage Group: {results['x_cgfg_LEMACNORM']:.4f} ({results['x_cgfg_LEMACNORM'] * 100:.2f}%)")
    print(f"Total EOW Aircraft: {results['x_cg_LEMACNORM']:.4f} ({results['x_cg_LEMACNORM'] * 100:.2f}%)")