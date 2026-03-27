import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import FormatStrFormatter

# --- 1. DATA IMPORT & CORE DEFINITIONS ---
import Input as it
import CG_positions as cg

# Aircraft physical data
OEW = it.EOW               
X_OEW = cg.x_cg            
MAC = cg.c_macw            
X_LEMAC = it.x_LEMACw      

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
row_positions = [X_ROW_1 + (i * ROW_PITCH) for i in range(NUM_ROWS)]

def add_mass(current_w, current_cg, added_w, added_cg):
    new_w = current_w + added_w
    new_cg = ((current_w * current_cg) + (added_w * added_cg)) / new_w
    return new_w, new_cg

# --- 2. GENERATE COORDINATES ---
pa_W = [OEW]; pa_CG = [X_OEW]
pb_W = [OEW]; pb_CG = [X_OEW]

# Cargo Loop
for m, x in [(MASS_FRONT_CARGO, X_FRONT_CARGO), (MASS_AFT_CARGO, X_AFT_CARGO)]:
    w, c = add_mass(pa_W[-1], pa_CG[-1], m, x)
    pa_W.append(w); pa_CG.append(c)
for m, x in [(MASS_AFT_CARGO, X_AFT_CARGO), (MASS_FRONT_CARGO, X_FRONT_CARGO)]:
    w, c = add_mass(pb_W[-1], pb_CG[-1], m, x)
    pb_W.append(w); pb_CG.append(c)

# Window Seats Loop
for x in row_positions:
    w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
    pa_W.append(w); pa_CG.append(c)
for x in reversed(row_positions):
    w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
    pb_W.append(w); pb_CG.append(c)

# Aisle Seats Loop
for x in row_positions:
    w, c = add_mass(pa_W[-1], pa_CG[-1], 2 * MASS_PAX, x)
    pa_W.append(w); pa_CG.append(c)
for x in reversed(row_positions):
    w, c = add_mass(pb_W[-1], pb_CG[-1], 2 * MASS_PAX, x)
    pb_W.append(w); pb_CG.append(c)

# Fuel Loading
f_W = [pa_W[-1]]; f_CG = [pa_CG[-1]]
for f in np.linspace(0, MAX_FUEL, 40)[1:]:
    if f_W[0] + f <= MTOW:
        w, c = add_mass(f_W[0], f_CG[0], f, X_FUEL)
        f_W.append(w); f_CG.append(c)
    else:
        w, c = add_mass(f_W[0], f_CG[0], MTOW - f_W[0], X_FUEL)
        f_W.append(w); f_CG.append(c)
        break

# Convert to MAC fraction
pa_mac = [((c - X_LEMAC) / MAC) for c in pa_CG]
pb_mac = [((c - X_LEMAC) / MAC) for c in pb_CG]
f_mac = [((c - X_LEMAC) / MAC) for c in f_CG]

# --- 3. ANIMATION SETUP ---
plt.style.use('dark_background') 
fig, ax = plt.subplots(figsize=(12, 8))
ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))

# Neon Color Palette
c_cargo, c_win, c_ais, c_fuel = '#9D4EDD', '#4895EF', '#F72585', '#4CC9F0'

l_cargo_a, = ax.plot([], [], color=c_cargo, marker='o', markersize=4, label='Cargo')
l_cargo_b, = ax.plot([], [], color=c_cargo, marker='o', markersize=4)
l_win_a, = ax.plot([], [], color=c_win, marker='o', markersize=3, label='Window Pax')
l_win_b, = ax.plot([], [], color=c_win, marker='o', markersize=3)
l_ais_a, = ax.plot([], [], color=c_ais, marker='o', markersize=3, label='Aisle Pax')
l_ais_b, = ax.plot([], [], color=c_ais, marker='o', markersize=3)
l_fuel, = ax.plot([], [], color=c_fuel, linewidth=4, label='Fuel Loading')

ax.scatter([pa_mac[0]], [OEW], color='white', s=100, zorder=5, label='OEW CG')

ax.set_xlim(min(pa_mac)-0.05, max(pb_mac)+0.1)
ax.set_ylim(OEW - 1000, MTOW + 2000)

# UPDATED HEADER
ax.set_title("CRJ-1000 Potato Diagram", fontsize=16, color='white', fontweight='bold', pad=20)

ax.set_xlabel("$x_{cg} / MAC$", fontsize=12); ax.set_ylabel("Mass (kg)", fontsize=12)
ax.legend(loc='upper left', frameon=True, facecolor='#222')
ax.grid(True, alpha=0.15)

# Horizontal limit lines
ax.axhline(y=MTOW, color='red', linestyle='--', alpha=0.5)
ax.text(ax.get_xlim()[1], MTOW, ' MTOW', color='red', va='center', fontweight='bold')

def update(frame):
    # Cargo (0-2)
    if frame <= 2:
        l_cargo_a.set_data(pa_mac[:frame+1], pa_W[:frame+1])
        l_cargo_b.set_data(pb_mac[:frame+1], pb_W[:frame+1])
    # Window (3-27)
    elif frame <= 27:
        l_win_a.set_data(pa_mac[2:frame+1], pa_W[2:frame+1])
        l_win_b.set_data(pb_mac[2:frame+1], pb_W[2:frame+1])
    # Aisle (28-52)
    elif frame <= 52:
        l_ais_a.set_data(pa_mac[27:frame+1], pa_W[27:frame+1])
        l_ais_b.set_data(pb_mac[27:frame+1], pb_W[27:frame+1])
    # Fuel (53+)
    else:
        fuel_idx = frame - 52
        if fuel_idx < len(f_mac):
            l_fuel.set_data(f_mac[:fuel_idx+1], f_W[:fuel_idx+1])
    return l_cargo_a, l_cargo_b, l_win_a, l_win_b, l_ais_a, l_ais_b, l_fuel

total_frames = 52 + len(f_mac) + 30 # Extra frames to stay at the end
ani = FuncAnimation(fig, update, frames=total_frames, interval=50, blit=True, repeat=False)

plt.tight_layout()
plt.show()