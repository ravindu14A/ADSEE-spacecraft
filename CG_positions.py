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
WEIGHT_UNACCOUNTED = EOW - (WEIGHT_fg + WEIGHT_wg)

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

    # Unaccounted mass is typically placed at the aircraft empty weight CG
    x_cg_unaccounted = x_cg

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
    x_unaccounted_LEMAC = x_cg_unaccounted - x_LEMACw

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
    x_unaccounted_LEMACNORM = x_unaccounted_LEMAC / c_macw

    return {
        "from_nose": {
            "components": {"Wing": x_cgw, "Horizontal Tail": x_cgh, "Vertical Tail": x_cgv, "Fuselage": x_cgfus,
                           "Propulsion Sys": x_cgn, "Main Landing Gear": x_MG, "Nose Landing Gear": x_NW,
                           "Cockpit Systems": x_cockpit},
            "groups": {"Wing Group": x_cgwg, "Fuselage Group": x_cgfg, "Unaccounted Group": x_cg_unaccounted},
            "aircraft": x_cg
        },
        "from_lemac": {
            "components": {"Wing": x_cgw_LEMAC, "Horizontal Tail": x_cgh_LEMAC, "Vertical Tail": x_cgv_LEMAC,
                           "Fuselage": x_cgfus_LEMAC, "Propulsion Sys": x_cgn_LEMAC, "Main Landing Gear": x_MG_LEMAC,
                           "Nose Landing Gear": x_NW_LEMAC, "Cockpit Systems": x_cockpit_LEMAC},
            "groups": {"Wing Group": x_cgwg_LEMAC, "Fuselage Group": x_cgfg_LEMAC,
                       "Unaccounted Group": x_unaccounted_LEMAC},
            "aircraft": x_cg_LEMAC
        },
        "percent_mac": {
            "components": {"Wing": x_cgw_LEMACNORM, "Horizontal Tail": x_cgh_LEMACNORM,
                           "Vertical Tail": x_cgv_LEMACNORM, "Fuselage": x_cgfus_LEMACNORM,
                           "Propulsion Sys": x_cgn_LEMACNORM,
                           "Main Landing Gear": x_MG_LEMACNORM, "Nose Landing Gear": x_NW_LEMACNORM,
                           "Cockpit Systems": x_cockpit_LEMACNORM},
            "groups": {"Wing Group": x_cgwg_LEMACNORM, "Fuselage Group": x_cgfg_LEMACNORM,
                       "Unaccounted Group": x_unaccounted_LEMACNORM},
            "aircraft": x_cg_LEMACNORM
        },
        "mass_kg": {
            "components": {"Wing": WEIGHT_WING, "Horizontal Tail": WEIGHT_HORIZONTAL_TAIL,
                           "Vertical Tail": WEIGHT_VERTICAL_TAIL, "Fuselage": WEIGHT_FUSELAGE,
                           "Propulsion Sys": WEIGHT_PROPULSION_SYSTEM, "Main Landing Gear": WEIGHT_MAIN_LANDING_GEAR,
                           "Nose Landing Gear": WEIGHT_NOSE_LANDING_GEAR, "Cockpit Systems": WEIGHT_COCKPIT_SYSTEMS},
            "groups": {"Wing Group": WEIGHT_wg, "Fuselage Group": WEIGHT_fg, "Unaccounted Group": WEIGHT_UNACCOUNTED},
            "aircraft": EOW
        },
        "mass_pct": {
            "components": {"Wing": WEIGHT_WING / EOW * 100, "Horizontal Tail": WEIGHT_HORIZONTAL_TAIL / EOW * 100,
                           "Vertical Tail": WEIGHT_VERTICAL_TAIL / EOW * 100, "Fuselage": WEIGHT_FUSELAGE / EOW * 100,
                           "Propulsion Sys": WEIGHT_PROPULSION_SYSTEM / EOW * 100,
                           "Main Landing Gear": WEIGHT_MAIN_LANDING_GEAR / EOW * 100,
                           "Nose Landing Gear": WEIGHT_NOSE_LANDING_GEAR / EOW * 100,
                           "Cockpit Systems": WEIGHT_COCKPIT_SYSTEMS / EOW * 100},
            "groups": {"Wing Group": WEIGHT_wg / EOW * 100, "Fuselage Group": WEIGHT_fg / EOW * 100,
                       "Unaccounted Group": WEIGHT_UNACCOUNTED / EOW * 100},
            "aircraft": 100.0
        }
    }


def print_cg_table(results):
    print("\n" + "=" * 115)
    print(" " * 45 + "BASELINE CG REPORT (FULL DATA)")
    print("=" * 115)
    print(
        f"{'COMPONENT / GROUP':<25} | {'Mass (% EOW)':<13} | {'Mass (kg)':<12} | {'CG from Nose (m)':<17} | {'CG from LEMAC (m)':<18} | {'CG as % MAC':<15}")
    print("-" * 115)

    print("COMPONENTS:")
    # Print the specific components needed for the table, in the order of the target table style
    target_components = ["Wing", "Horizontal Tail", "Vertical Tail", "Fuselage",
                         "Main Landing Gear", "Nose Landing Gear", "Propulsion Sys", "Cockpit Systems"]

    for comp in target_components:
        mass_pct = results['mass_pct']['components'][comp]
        mass_kg = results['mass_kg']['components'][comp]
        nose = results['from_nose']['components'][comp]
        lemac = results['from_lemac']['components'][comp]
        mac = results['percent_mac']['components'][comp] * 100
        print(f"  {comp:<23} | {mass_pct:<13.1f} | {mass_kg:<12.2f} | {nose:<17.4f} | {lemac:<18.4f} | {mac:<14.2f}%")

    print("-" * 115)

    print("ASSEMBLY GROUPS:")
    target_groups = ["Fuselage Group", "Wing Group", "Unaccounted Group"]
    for grp in target_groups:
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