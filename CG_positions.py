import numpy as np
import Input as it

# =====================================================================
# CONSTANTS & PRE-CALCULATIONS (Independent of x_LEMACw)
# =====================================================================

x_cockpit = it.x_cockpit
x_NW = it.x_NW
x_MG = it.x_MG
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
# COMPONENT WEIGHTS (Table Values Only)
# ------------------------------------
WEIGHT_WING = it.WEIGHT_WINGp / 100 * EOW
WEIGHT_HORIZONTAL_TAIL = it.WEIGHT_HORIZONTAL_TAILp / 100 * EOW
WEIGHT_VERTICAL_TAIL = it.WEIGHT_VERTICAL_TAILp / 100 * EOW
WEIGHT_FUSELAGE = it.WEIGHT_FUSELAGEp / 100 * EOW
WEIGHT_MAIN_LANDING_GEAR = it.WEIGHT_MAIN_LANDING_GEARp / 100 * EOW
WEIGHT_NOSE_LANDING_GEAR = it.WEIGHT_NOSE_LANDING_GEARp / 100 * EOW
WEIGHT_PROPULSION_SYSTEM = it.WEIGHT_PROPULSION_SYSTEMp / 100 * EOW
WEIGHT_COCKPIT_SYSTEMS = it.WEIGHT_COCKPIT_SYSTEMSp / 100 * EOW

WEIGHT_fg = WEIGHT_FUSELAGE + WEIGHT_COCKPIT_SYSTEMS + WEIGHT_PROPULSION_SYSTEM + WEIGHT_HORIZONTAL_TAIL + WEIGHT_VERTICAL_TAIL + WEIGHT_NOSE_LANDING_GEAR
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

# ---- WING CG CORRECTION ----
y_cgw = 0.35 * b_w / 2

# 1. Calculate the full aerodynamic local chord at y_cgw
c_local = c_rw * (1 - (1 - TAPER_RATIOw) * 0.35)

# 2. Define the structural wing box boundaries (typical transport fractions)
front_spar_fraction = it.front_spar_fraction
rear_spar_fraction = it.rear_spar_fraction

x_front_spar = front_spar_fraction * c_local
x_rear_spar = rear_spar_fraction * c_local

# 3. Calculate structural chord (c_s) as defined in the Torenbeek diagram
c_s_structural = x_rear_spar - x_front_spar

# 4. Calculate absolute distances
distance_LEMAC_to_local_LE = (y_cgw - y_macw) * np.tan(np.radians(SWEEP_ANGLEw))

# 5. Apply the 0.7 multiplier exclusively to the structural chord, starting from the front spar
x_cgw_relative = distance_LEMAC_to_local_LE + x_front_spar + (0.7 * c_s_structural)
# ----------------------------

x_cgh_relative = 0.42 * c_mach
y_cgh = 0.38 * b_h / 2

x_cgv_relative = 0.42 * c_macv
z_cgv_relative = 0.38 * b_v

x_cgn_relative = 0.4 * l_nac

x_cgh = x_LEMACh + x_cgh_relative
x_cgv = x_LEMACv + x_cgv_relative
x_cgfus = x_cgfusratio * l_fus
x_cgn = x_startnacelle + x_cgn_relative

x_cgfg = (x_cgfus * WEIGHT_FUSELAGE +
          x_cockpit * WEIGHT_COCKPIT_SYSTEMS +
          x_cgn * WEIGHT_PROPULSION_SYSTEM +
          x_cgh * WEIGHT_HORIZONTAL_TAIL +
          x_cgv * WEIGHT_VERTICAL_TAIL +
          x_NW * WEIGHT_NOSE_LANDING_GEAR) / WEIGHT_fg


def calculate_aircraft_cgs(x_LEMACw):
    x_cgw = x_LEMACw + x_cgw_relative
    x_cgwg = (x_cgw * WEIGHT_WING + x_MG * WEIGHT_MAIN_LANDING_GEAR) / WEIGHT_wg

    # This mathematical output is the true baseline CG per the assignment note
    x_cg = (x_cgfg * WEIGHT_fg + x_cgwg * WEIGHT_wg) / (WEIGHT_fg + WEIGHT_wg)

    x_cgw_LEMAC = x_cgw - x_LEMACw
    x_cgh_LEMAC = x_cgh - x_LEMACw
    x_cgv_LEMAC = x_cgv - x_LEMACw
    x_cgfus_LEMAC = x_cgfus - x_LEMACw
    x_cgn_LEMAC = x_cgn - x_LEMACw

    # Adding the missing components
    x_MG_LEMAC = x_MG - x_LEMACw
    x_NW_LEMAC = x_NW - x_LEMACw
    x_cockpit_LEMAC = x_cockpit - x_LEMACw

    x_cgfg_LEMAC = x_cgfg - x_LEMACw
    x_cgwg_LEMAC = x_cgwg - x_LEMACw
    x_cg_LEMAC = x_cg - x_LEMACw

    x_cgw_LEMACNORM = x_cgw_LEMAC / c_macw
    x_cgh_LEMACNORM = x_cgh_LEMAC / c_macw
    x_cgv_LEMACNORM = x_cgv_LEMAC / c_macw
    x_cgfus_LEMACNORM = x_cgfus_LEMAC / c_macw
    x_cgn_LEMACNORM = x_cgn_LEMAC / c_macw

    # Adding the missing components
    x_MG_LEMACNORM = x_MG_LEMAC / c_macw
    x_NW_LEMACNORM = x_NW_LEMAC / c_macw
    x_cockpit_LEMACNORM = x_cockpit_LEMAC / c_macw

    x_cgfg_LEMACNORM = x_cgfg_LEMAC / c_macw
    x_cgwg_LEMACNORM = x_cgwg_LEMAC / c_macw
    x_cg_LEMACNORM = x_cg_LEMAC / c_macw

    return {
        "from_nose": {
            "components": {"wing": x_cgw, "horizontal_stab": x_cgh, "vertical_stab": x_cgv, "fuselage": x_cgfus,
                           "engine": x_cgn, "main_landing_gear": x_MG, "nose_landing_gear": x_NW,
                           "cockpit_systems": x_cockpit},
            "groups": {"wing_group": x_cgwg, "fuselage_group": x_cgfg},
            "aircraft": x_cg
        },
        "from_lemac": {
            "components": {"wing": x_cgw_LEMAC, "horizontal_stab": x_cgh_LEMAC, "vertical_stab": x_cgv_LEMAC,
                           "fuselage": x_cgfus_LEMAC, "engine": x_cgn_LEMAC, "main_landing_gear": x_MG_LEMAC,
                           "nose_landing_gear": x_NW_LEMAC, "cockpit_systems": x_cockpit_LEMAC},
            "groups": {"wing_group": x_cgwg_LEMAC, "fuselage_group": x_cgfg_LEMAC},
            "aircraft": x_cg_LEMAC
        },
        "percent_mac": {
            "components": {"wing": x_cgw_LEMACNORM, "horizontal_stab": x_cgh_LEMACNORM,
                           "vertical_stab": x_cgv_LEMACNORM, "fuselage": x_cgfus_LEMACNORM, "engine": x_cgn_LEMACNORM,
                           "main_landing_gear": x_MG_LEMACNORM, "nose_landing_gear": x_NW_LEMACNORM,
                           "cockpit_systems": x_cockpit_LEMACNORM},
            "groups": {"wing_group": x_cgwg_LEMACNORM, "fuselage_group": x_cgfg_LEMACNORM},
            "aircraft": x_cg_LEMACNORM
        },
        "mass_kg": {
            "components": {"wing": WEIGHT_WING, "horizontal_stab": WEIGHT_HORIZONTAL_TAIL,
                           "vertical_stab": WEIGHT_VERTICAL_TAIL, "fuselage": WEIGHT_FUSELAGE,
                           "engine": WEIGHT_PROPULSION_SYSTEM, "main_landing_gear": WEIGHT_MAIN_LANDING_GEAR,
                           "nose_landing_gear": WEIGHT_NOSE_LANDING_GEAR, "cockpit_systems": WEIGHT_COCKPIT_SYSTEMS},
            "groups": {"wing_group": WEIGHT_wg, "fuselage_group": WEIGHT_fg},
            "aircraft": WEIGHT_wg + WEIGHT_fg
        },
        "mass_pct": {
            "components": {"wing": WEIGHT_WING / EOW * 100, "horizontal_stab": WEIGHT_HORIZONTAL_TAIL / EOW * 100,
                           "vertical_stab": WEIGHT_VERTICAL_TAIL / EOW * 100, "fuselage": WEIGHT_FUSELAGE / EOW * 100,
                           "engine": WEIGHT_PROPULSION_SYSTEM / EOW * 100,
                           "main_landing_gear": WEIGHT_MAIN_LANDING_GEAR / EOW * 100,
                           "nose_landing_gear": WEIGHT_NOSE_LANDING_GEAR / EOW * 100,
                           "cockpit_systems": WEIGHT_COCKPIT_SYSTEMS / EOW * 100},
            "groups": {"wing_group": WEIGHT_wg / EOW * 100, "fuselage_group": WEIGHT_fg / EOW * 100},
            "aircraft": (WEIGHT_wg + WEIGHT_fg) / EOW * 100
        }
    }


def print_cg_table(results):
    print("\n" + "=" * 115)
    print(" " * 45 + "BASELINE CG REPORT")
    print("=" * 115)
    print(
        f"{'COMPONENT / GROUP':<25} | {'Mass (% EOW)':<13} | {'Mass (kg)':<12} | {'CG from Nose (m)':<17} | {'CG from LEMAC (m)':<18} | {'CG as % MAC':<15}")
    print("-" * 115)

    print("COMPONENTS:")
    for comp in results['from_nose']['components']:
        mass_pct = results['mass_pct']['components'][comp]
        mass_kg = results['mass_kg']['components'][comp]
        nose = results['from_nose']['components'][comp]
        lemac = results['from_lemac']['components'][comp]
        mac = results['percent_mac']['components'][comp] * 100
        print(f"  {comp:<23} | {mass_pct:<13.1f} | {mass_kg:<12.2f} | {nose:<17.4f} | {lemac:<18.4f} | {mac:<14.2f}%")

    print("-" * 115)

    print("ASSEMBLY GROUPS:")
    for grp in results['from_nose']['groups']:
        mass_pct = results['mass_pct']['groups'][grp]
        mass_kg = results['mass_kg']['groups'][grp]
        nose = results['from_nose']['groups'][grp]
        lemac = results['from_lemac']['groups'][grp]
        mac = results['percent_mac']['groups'][grp] * 100
        print(f"  {grp:<23} | {mass_pct:<13.1f} | {mass_kg:<12.2f} | {nose:<17.4f} | {lemac:<18.4f} | {mac:<14.2f}%")

    print("=" * 115)

    mass_pct_total = results['mass_pct']['aircraft']
    mass_kg_total = results['mass_kg']['aircraft']
    nose_total = results['from_nose']['aircraft']
    lemac_total = results['from_lemac']['aircraft']
    mac_total = results['percent_mac']['aircraft'] * 100
    print(
        f"{'TOTAL EOW AIRCRAFT':<25} | {mass_pct_total:<13.1f} | {mass_kg_total:<12.2f} | {nose_total:<17.4f} | {lemac_total:<18.4f} | {mac_total:<14.2f}%")
    print("=" * 115)


if __name__ == '__main__':
    x_LEMACw_input = it.x_LEMACw
    results = calculate_aircraft_cgs(x_LEMACw_input)
    print_cg_table(results)
    print("\nCalculated MAC:", c_macw)
    print("x_LEMACw_input:", x_LEMACw_input)