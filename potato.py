import numpy as np
import matplotlib.pyplot as plt

# Import your existing data (ensure this script is in the same folder)
import Input as it
import CG_positions as cg

# ------------------------------------
# 1. DEFINE LOADING VARIABLES
# ------------------------------------
# Aircraft Empty Weight and CG (from your existing code)
OEW = it.EOW
X_OEW = cg.x_cg  # Absolute CG from nose at EOW
MAC = cg.c_macw
X_LEMAC = it.x_LEMACw

# Weight Limits & Fuel
MTOW = 41640          # kg
MAX_FUEL = 8822       # kg
X_FUEL = 20.92        # m (from nose)

# Payload Weights
MASS_PAX = 87         # kg per passenger
MASS_FRONT_CARGO = 472  # kg
X_FRONT_CARGO = 7.77  # m (from nose)
MASS_AFT_CARGO = 1294 # kg
X_AFT_CARGO = 19.71   # m (from nose)

# Cabin Layout (100 pax, 2+2 layout = 25 rows)
NUM_ROWS = 25
PAX_PER_ROW_GROUP = 2 # 2 Window pax, or 2 Aisle pax per row
ROW_PITCH = 0.7874    # 31 inches in meters
X_ROW_1 = 6.0         # Assumed start of passenger cabin from nose (Adjust this if you have a specific cabin start X)

# Calculate X coordinates for all 25 rows
row_positions = [X_ROW_1 + (i * ROW_PITCH) for i in range(NUM_ROWS)]


# ------------------------------------
# 2. HELPER FUNCTION TO ADD MASS
# ------------------------------------
def add_mass(current_weight, current_cg, added_weight, added_cg):
    """Calculates the new CG when a mass is added."""
    new_weight = current_weight + added_weight
    new_cg = ((current_weight * current_cg) + (added_weight * added_cg)) / new_weight
    return new_weight, new_cg


# ------------------------------------
# 3. PATH A: MOST FORWARD CG LIMIT (Front to Back)
# ------------------------------------
path_a_W = [OEW]
path_a_CG = [X_OEW]

# 1. Add Front Cargo
w, c = add_mass(path_a_W[-1], path_a_CG[-1], MASS_FRONT_CARGO, X_FRONT_CARGO)
path_a_W.append(w); path_a_CG.append(c)

# 2. Add Window Pax (Front to Back)
for x_row in row_positions:
    w, c = add_mass(path_a_W[-1], path_a_CG[-1], PAX_PER_ROW_GROUP * MASS_PAX, x_row)
    path_a_W.append(w); path_a_CG.append(c)

# 3. Add Aisle Pax (Front to Back)
for x_row in row_positions:
    w, c = add_mass(path_a_W[-1], path_a_CG[-1], PAX_PER_ROW_GROUP * MASS_PAX, x_row)
    path_a_W.append(w); path_a_CG.append(c)

# 4. Add Aft Cargo (Reaching Actual MZFW)
w, c = add_mass(path_a_W[-1], path_a_CG[-1], MASS_AFT_CARGO, X_AFT_CARGO)
path_a_W.append(w); path_a_CG.append(c)


# ------------------------------------
# 4. PATH B: MOST AFT CG LIMIT (Back to Front)
# ------------------------------------
path_b_W = [OEW]
path_b_CG = [X_OEW]

# 1. Add Aft Cargo
w, c = add_mass(path_b_W[-1], path_b_CG[-1], MASS_AFT_CARGO, X_AFT_CARGO)
path_b_W.append(w); path_b_CG.append(c)

# 2. Add Window Pax (Back to Front)
for x_row in reversed(row_positions):
    w, c = add_mass(path_b_W[-1], path_b_CG[-1], PAX_PER_ROW_GROUP * MASS_PAX, x_row)
    path_b_W.append(w); path_b_CG.append(c)

# 3. Add Aisle Pax (Back to Front)
for x_row in reversed(row_positions):
    w, c = add_mass(path_b_W[-1], path_b_CG[-1], PAX_PER_ROW_GROUP * MASS_PAX, x_row)
    path_b_W.append(w); path_b_CG.append(c)

# 4. Add Front Cargo (Reaching Actual MZFW)
w, c = add_mass(path_b_W[-1], path_b_CG[-1], MASS_FRONT_CARGO, X_FRONT_CARGO)
path_b_W.append(w); path_b_CG.append(c)


# ------------------------------------
# 5. ADD FUEL UP TO MTOW
# ------------------------------------
actual_MZFW = path_a_W[-1]
fuel_W = [actual_MZFW]
fuel_CG = [path_a_CG[-1]] # Fuel loads from the top of the payload envelope

# Add fuel in small increments for a smooth line
fuel_increments = np.linspace(0, MAX_FUEL, 50)
for added_fuel in fuel_increments[1:]: # Skip 0
    if fuel_W[0] + added_fuel <= MTOW:
        w, c = add_mass(fuel_W[0], fuel_CG[0], added_fuel, X_FUEL)
        fuel_W.append(w); fuel_CG.append(c)
    else:
        # If adding fuel exceeds MTOW, calculate exact fillable limit and stop
        remaining_allowable_fuel = MTOW - fuel_W[0]
        w, c = add_mass(fuel_W[0], fuel_CG[0], remaining_allowable_fuel, X_FUEL)
        fuel_W.append(w); fuel_CG.append(c)
        break


# ------------------------------------
# 6. CONVERT ALL CGs TO % MAC
# ------------------------------------
def to_percent_mac(cg_list):
    return [((cg - X_LEMAC) / MAC) * 100 for cg in cg_list]

path_a_mac = to_percent_mac(path_a_CG)
path_b_mac = to_percent_mac(path_b_CG)
fuel_mac = to_percent_mac(fuel_CG)


# ------------------------------------
# 7. PLOT THE LOADING DIAGRAM
# ------------------------------------
plt.figure(figsize=(10, 8))

# Plot the loading paths
plt.plot(path_a_mac, path_a_W, 'b-', label='Forward Loading Limit (Front-to-Back)', marker='.')
plt.plot(path_b_mac, path_b_W, 'r-', label='Aft Loading Limit (Back-to-Front)', marker='.')
plt.plot(fuel_mac, fuel_W, 'g-', linewidth=2, label='Fuel Loading (Capped at MTOW)')

# Plot reference points
plt.axhline(y=OEW, color='k', linestyle='--', alpha=0.5, label='OEW (23,188 kg)')
plt.axhline(y=actual_MZFW, color='orange', linestyle='--', alpha=0.5, label=f'Calculated MZFW ({int(actual_MZFW)} kg)')
plt.axhline(y=MTOW, color='m', linestyle='--', alpha=0.8, label=f'MTOW ({MTOW} kg)')

# Add a point for the empty aircraft CG
plt.scatter([to_percent_mac([X_OEW])[0]], [OEW], color='black', zorder=5, s=100, label='CG @ OEW')

# Formatting the chart
plt.title('Aircraft Loading Diagram (Potato Diagram) - Task D', fontsize=14, fontweight='bold')
plt.xlabel('Center of Gravity (% MAC)', fontsize=12)
plt.ylabel('Mass (kg)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='best')

# Show limits
min_cg = min(min(path_a_mac), min(path_b_mac), min(fuel_mac))
max_cg = max(max(path_a_mac), max(path_b_mac), max(fuel_mac))
plt.xlim(min_cg - 5, max_cg + 5)

plt.tight_layout()
plt.show()

print(f"Max Forward CG: {min_cg:.2f} % MAC")
print(f"Max Aft CG: {max_cg:.2f} % MAC")