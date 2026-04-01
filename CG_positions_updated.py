import numpy as np
import Input_updated as it
import CG_positions as base

# =====================================================================
# CONSTANTS & PRE-CALCULATIONS (Inherited to maintain namespace)
# =====================================================================

x_cockpit = it.x_cockpit
x_NW = it.x_NW
x_MG = it.x_MG

x_BATT_FRONT = it.X_BATT_FRONT
x_BATT_AFT = it.X_BATT_AFT

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
# COMPONENT WEIGHTS (Updated from EXX Input)
# ------------------------------------
WEIGHT_WING = it.WEIGHT_WING
WEIGHT_HORIZONTAL_TAIL = it.WEIGHT_HORIZONTAL_TAIL
WEIGHT_VERTICAL_TAIL = it.WEIGHT_VERTICAL_TAIL
WEIGHT_FUSELAGE = it.WEIGHT_FUSELAGE
WEIGHT_MAIN_LANDING_GEAR = it.WEIGHT_MAIN_LANDING_GEAR
WEIGHT_NOSE_LANDING_GEAR = it.WEIGHT_NOSE_LANDING_GEAR
WEIGHT_PROPULSION_SYSTEM = it.WEIGHT_PROPULSION_SYSTEM
WEIGHT_COCKPIT_SYSTEMS = it.WEIGHT_COCKPIT_SYSTEMS

WEIGHT_UNACCOUNTED = it.WEIGHT_UNACCOUNTED
WEIGHT_BATT_FRONT = it.MASS_BATT_FRONT
WEIGHT_BATT_AFT = it.MASS_BATT_AFT

# Baseline Group Weights for EXX (Pre-Battery, Pre-Unaccounted)
WEIGHT_fg_base = (WEIGHT_FUSELAGE + WEIGHT_COCKPIT_SYSTEMS + WEIGHT_PROPULSION_SYSTEM +
                  WEIGHT_HORIZONTAL_TAIL + WEIGHT_VERTICAL_TAIL + WEIGHT_NOSE_LANDING_GEAR)
WEIGHT_wg = WEIGHT_WING + WEIGHT_MAIN_LANDING_GEAR

# Final Fuselage Group Weight (Includes Batteries and Unaccounted)
WEIGHT_fg_exx = WEIGHT_fg_base + WEIGHT_UNACCOUNTED + WEIGHT_BATT_FRONT + WEIGHT_BATT_AFT

# Calculate Total EOW equivalent for mass percentages
TOTAL_MASS_EOW = WEIGHT_fg_exx + WEIGHT_wg

# ------------------------------------
# CALCULATED DIMENSIONS
# ------------------------------------
c_macw = base.c_macw
c_mach = base.c_mach
c_macv = base.c_macv

y_macw = base.y_macw
y_mach = base.y_mach
z_macv = base.z_macv

# ---- EXPLICIT WING CG CORRECTION OVERRIDE ----
y_cgw = 0.35 * b_w / 2

# 1. Calculate the full aerodynamic local chord at y_cgw
c_local = c_rw * (1 - (1 - TAPER_RATIOw) * 0.35)

# 2. Define the structural wing box boundaries (typical transport fractions)
front_spar_fraction = it.front_spar_fraction
rear_spar_fraction = base.rear_spar_fraction

x_front_spar = front_spar_fraction * c_local
x_rear_spar = rear_spar_fraction * c_local

# 3. Calculate structural chord (c_s) as defined in the Torenbeek diagram
c_s_structural = x_rear_spar - x_front_spar

# 4. Calculate absolute distances
distance_LEMAC_to_local_LE = (y_cgw - y_macw) * np.tan(np.radians(SWEEP_ANGLEw))

# 5. Apply the 0.7 multiplier exclusively to the structural chord, starting from the front spar
x_cgw_relative = distance_LEMAC_to_local_LE + x_front_spar + (0.7 * c_s_structural)
# ----------------------------------------------

x_cgh_relative = base.x_cgh_relative
y_cgh = base.y_cgh

x_cgv_relative = base.x_cgv_relative
z_cgv_relative = base.z_cgv_relative

x_cgn_relative = base.x_cgn_relative

x_cgh = base.x_cgh
x_cgv = base.x_cgv
x_cgfus = base.x_cgfus

# Anchored to base per Point II (Engine CG does not change)
x_cgn = base.x_cgn

# New EXX specific battery locations
x_cgbat_front = it.X_BATT_FRONT
x_cgbat_aft = it.X_BATT_AFT

# Baseline Fuselage CG (Using base weights without battery or unaccounted mass)
x_cgfg_base = (x_cgfus * WEIGHT_FUSELAGE +
               x_cockpit * WEIGHT_COCKPIT_SYSTEMS +
               x_cgn * WEIGHT_PROPULSION_SYSTEM +
               x_cgh * WEIGHT_HORIZONTAL_TAIL +
               x_cgv * WEIGHT_VERTICAL_TAIL +
               x_NW * WEIGHT_NOSE_LANDING_GEAR) / WEIGHT_fg_base


def calculate_aircraft_cgs(x_LEMACw):
    x_cgw = x_LEMACw + x_cgw_relative
    x_cgwg = (x_cgw * WEIGHT_WING + x_MG * WEIGHT_MAIN_LANDING_GEAR) / WEIGHT_wg

    # Fetch the original aircraft's absolute CG to serve as the anchor for the missing mass
    original_cgs = base.calculate_aircraft_cgs(x_LEMACw)
    x_cg_unaccounted = original_cgs['from_nose']['aircraft']

    # Integrate batteries and unaccounted mass directly into the Fuselage Group
    x_cgfg_exx = (x_cgfg_base * WEIGHT_fg_base +
                  x_cg_unaccounted * WEIGHT_UNACCOUNTED +
                  x_cgbat_front * WEIGHT_BATT_FRONT +
                  x_cgbat_aft * WEIGHT_BATT_AFT) / WEIGHT_fg_exx

    # Final EXX Total CG
    x_cg_exx = (x_cgfg_exx * WEIGHT_fg_exx + x_cgwg * WEIGHT_wg) / (WEIGHT_fg_exx + WEIGHT_wg)

    x_cgw_LEMAC = x_cgw - x_LEMACw
    x_cgh_LEMAC = x_cgh - x_LEMACw
    x_cgv_LEMAC = x_cgv - x_LEMACw
    x_cgfus_LEMAC = x_cgfus - x_LEMACw
    x_cgn_LEMAC = x_cgn - x_LEMACw
    x_cgbat_front_LEMAC = x_cgbat_front - x_LEMACw
    x_cgbat_aft_LEMAC = x_cgbat_aft - x_LEMACw

    # Adding missing components for table output
    x_MG_LEMAC = x_MG - x_LEMACw
    x_NW_LEMAC = x_NW - x_LEMACw
    x_cockpit_LEMAC = x_cockpit - x_LEMACw
    x_unaccounted_LEMAC = x_cg_unaccounted - x_LEMACw

    x_cgfg_LEMAC = x_cgfg_exx - x_LEMACw
    x_cgwg_LEMAC = x_cgwg - x_LEMACw
    x_cg_LEMAC = x_cg_exx - x_LEMACw

    x_cgw_LEMACNORM = x_cgw_LEMAC / c_macw
    x_cgh_LEMACNORM = x_cgh_LEMAC / c_macw
    x_cgv_LEMACNORM = x_cgv_LEMAC / c_macw
    x_cgfus_LEMACNORM = x_cgfus_LEMAC / c_macw
    x_cgn_LEMACNORM = x_cgn_LEMAC / c_macw
    x_cgbat_front_LEMACNORM = x_cgbat_front_LEMAC / c_macw
    x_cgbat_aft_LEMACNORM = x_cgbat_aft_LEMAC / c_macw

    # Adding missing components for table output
    x_MG_LEMACNORM = x_MG_LEMAC / c_macw
    x_NW_LEMACNORM = x_NW_LEMAC / c_macw
    x_cockpit_LEMACNORM = x_cockpit_LEMAC / c_macw
    x_unaccounted_LEMACNORM = x_unaccounted_LEMAC / c_macw

    x_cgfg_LEMACNORM = x_cgfg_LEMAC / c_macw
    x_cgwg_LEMACNORM = x_cgwg_LEMAC / c_macw
    x_cg_LEMACNORM = x_cg_LEMAC / c_macw

    return {
        "from_nose": {
            "components": {"Wing": x_cgw, "Horizontal Tail": x_cgh, "Vertical Tail": x_cgv,
                           "Fuselage": x_cgfus, "Propulsion Sys": x_cgn,
                           "Battery Front": x_cgbat_front, "Battery Aft": x_cgbat_aft,
                           "Main Landing Gear": x_MG, "Nose Landing Gear": x_NW, "Cockpit Systems": x_cockpit},
            "groups": {"Wing Group": x_cgwg, "Fuselage Group": x_cgfg_exx, "Unaccounted Group": x_cg_unaccounted},
            "aircraft": x_cg_exx
        },
        "from_lemac": {
            "components": {"Wing": x_cgw_LEMAC, "Horizontal Tail": x_cgh_LEMAC, "Vertical Tail": x_cgv_LEMAC,
                           "Fuselage": x_cgfus_LEMAC, "Propulsion Sys": x_cgn_LEMAC,
                           "Battery Front": x_cgbat_front_LEMAC, "Battery Aft": x_cgbat_aft_LEMAC,
                           "Main Landing Gear": x_MG_LEMAC, "Nose Landing Gear": x_NW_LEMAC,
                           "Cockpit Systems": x_cockpit_LEMAC},
            "groups": {"Wing Group": x_cgwg_LEMAC, "Fuselage Group": x_cgfg_LEMAC,
                       "Unaccounted Group": x_unaccounted_LEMAC},
            "aircraft": x_cg_LEMAC
        },
        "percent_mac": {
            "components": {"Wing": x_cgw_LEMACNORM, "Horizontal Tail": x_cgh_LEMACNORM,
                           "Vertical Tail": x_cgv_LEMACNORM, "Fuselage": x_cgfus_LEMACNORM,
                           "Propulsion Sys": x_cgn_LEMACNORM, "Battery Front": x_cgbat_front_LEMACNORM,
                           "Battery Aft": x_cgbat_aft_LEMACNORM,
                           "Main Landing Gear": x_MG_LEMACNORM, "Nose Landing Gear": x_NW_LEMACNORM,
                           "Cockpit Systems": x_cockpit_LEMACNORM},
            "groups": {"Wing Group": x_cgwg_LEMACNORM, "Fuselage Group": x_cgfg_LEMACNORM,
                       "Unaccounted Group": x_unaccounted_LEMACNORM},
            "aircraft": x_cg_LEMACNORM
        },
        "mass_kg": {
            "components": {"Wing": WEIGHT_WING, "Horizontal Tail": WEIGHT_HORIZONTAL_TAIL,
                           "Vertical Tail": WEIGHT_VERTICAL_TAIL, "Fuselage": WEIGHT_FUSELAGE,
                           "Propulsion Sys": WEIGHT_PROPULSION_SYSTEM, "Battery Front": WEIGHT_BATT_FRONT,
                           "Battery Aft": WEIGHT_BATT_AFT, "Main Landing Gear": WEIGHT_MAIN_LANDING_GEAR,
                           "Nose Landing Gear": WEIGHT_NOSE_LANDING_GEAR, "Cockpit Systems": WEIGHT_COCKPIT_SYSTEMS},
            "groups": {"Wing Group": WEIGHT_wg, "Fuselage Group": WEIGHT_fg_exx,
                       "Unaccounted Group": WEIGHT_UNACCOUNTED},
            "aircraft": TOTAL_MASS_EOW
        },
        "mass_pct": {
            "components": {"Wing": WEIGHT_WING / TOTAL_MASS_EOW * 100,
                           "Horizontal Tail": WEIGHT_HORIZONTAL_TAIL / TOTAL_MASS_EOW * 100,
                           "Vertical Tail": WEIGHT_VERTICAL_TAIL / TOTAL_MASS_EOW * 100,
                           "Fuselage": WEIGHT_FUSELAGE / TOTAL_MASS_EOW * 100,
                           "Propulsion Sys": WEIGHT_PROPULSION_SYSTEM / TOTAL_MASS_EOW * 100,
                           "Battery Front": WEIGHT_BATT_FRONT / TOTAL_MASS_EOW * 100,
                           "Battery Aft": WEIGHT_BATT_AFT / TOTAL_MASS_EOW * 100,
                           "Main Landing Gear": WEIGHT_MAIN_LANDING_GEAR / TOTAL_MASS_EOW * 100,
                           "Nose Landing Gear": WEIGHT_NOSE_LANDING_GEAR / TOTAL_MASS_EOW * 100,
                           "Cockpit Systems": WEIGHT_COCKPIT_SYSTEMS / TOTAL_MASS_EOW * 100},
            "groups": {"Wing Group": WEIGHT_wg / TOTAL_MASS_EOW * 100,
                       "Fuselage Group": WEIGHT_fg_exx / TOTAL_MASS_EOW * 100,
                       "Unaccounted Group": WEIGHT_UNACCOUNTED / TOTAL_MASS_EOW * 100},
            "aircraft": 100.0
        }
    }


def print_cg_table(results):
    print("\n" + "=" * 115)
    print(" " * 45 + "EXX VARIANT CG REPORT (FULL DATA)")
    print("=" * 115)
    print(
        f"{'COMPONENT / GROUP':<25} | {'Mass (% EOW)':<13} | {'Mass (kg)':<12} | {'CG from Nose (m)':<17} | {'CG from LEMAC (m)':<18} | {'CG as % MAC':<15}")
    print("-" * 115)

    print("COMPONENTS:")
    # Print the specific components needed for the table, in the order of the table
    target_components = ["Wing", "Horizontal Tail", "Vertical Tail", "Fuselage",
                         "Main Landing Gear", "Nose Landing Gear", "Propulsion Sys", "Cockpit Systems"]

    for comp in target_components:
        mass_pct = results['mass_pct']['components'][comp]
        mass_kg = results['mass_kg']['components'][comp]
        nose = results['from_nose']['components'][comp]
        lemac = results['from_lemac']['components'][comp]
        mac = results['percent_mac']['components'][comp] * 100
        print(f"  {comp:<23} | {mass_pct:<13.1f} | {mass_kg:<12.2f} | {nose:<17.4f} | {lemac:<18.4f} | {mac:<14.2f}%")

    print("\nNEW COMPONENTS:")
    new_components = ["Battery Front", "Battery Aft"]
    for comp in new_components:
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
        f"{'TOTAL AIRCRAFT (EOW+BATT)':<25} | {mass_pct_total:<13.1f} | {mass_kg_total:<12.2f} | {nose_total:<17.4f} | {lemac_total:<18.4f} | {mac_total:<14.2f}%")
    print("=" * 115)


if __name__ == '__main__':
    x_LEMACw_input = it.x_LEMACw
    results = calculate_aircraft_cgs(x_LEMACw_input)
    print_cg_table(results)