import numpy as np

# ------------------------------------
# ATMOSPHERIC CONSTANTS
# ------------------------------------
R = 287.05287      # Specific gas constant for dry air (J/(kg*K))
gamma = 1.4        # Ratio of specific heats
T0 = 288.15        # Sea level temperature (K)
P0 = 101325.0      # Sea level standard pressure (Pa)
g0 = 9.80665       # Standard gravitational acceleration (m/s^2)

def get_atmosphere_properties(h):
    """
    Calculates the speed of sound and air density at a given altitude h (in meters)
    using the ISA temperature and pressure models.
    Returns: (speed_of_sound, density)
    """
    # Layer 0: Troposphere (0 to 11,000 m)
    h_base0 = 0.0
    T_base0 = T0
    P_base0 = P0
    a0 = -0.0065 # Lapse rate (K/m)

    # Layer 1: Tropopause (11,000 to 20,000 m)
    h_base1 = 11000.0
    T_base1 = T_base0 + a0 * (h_base1 - h_base0)
    # Pressure at the top of the Troposphere (base of Tropopause)
    P_base1 = P_base0 * (T_base1 / T_base0) ** (-g0 / (a0 * R))

    # Layer 2: Stratosphere 1 (20,000 to 32,000 m)
    h_base2 = 20000.0
    T_base2 = T_base1
    a2 = 0.001 # Lapse rate (K/m)
    # Pressure at the top of the Tropopause (base of Stratosphere 1)
    # Uses isothermal pressure equation
    P_base2 = P_base1 * np.exp(-g0 / (R * T_base1) * (h_base2 - h_base1))

    # Determine temperature and pressure based on altitude
    if h < h_base1:
        T = T_base0 + a0 * (h - h_base0)
        P = P_base0 * (T / T_base0) ** (-g0 / (a0 * R))
    elif h < h_base2:
        T = T_base1
        P = P_base1 * np.exp(-g0 / (R * T_base1) * (h - h_base1))
    else:
        # Stratosphere 1 (Valid up to 32,000m)
        T = T_base2 + a2 * (h - h_base2)
        P = P_base2 * (T / T_base2) ** (-g0 / (a2 * R))

    # Calculate speed of sound and density
    a = np.sqrt(gamma * R * T)
    rho = P / (R * T)

    return a, rho