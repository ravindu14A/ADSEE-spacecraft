import numpy as np

# ------------------------------------
# ATMOSPHERIC CONSTANTS
# ------------------------------------
R = 287.05287      # Specific gas constant for dry air (J/(kg*K))
gamma = 1.4        # Ratio of specific heats
T0 = 288.15        # Sea level temperature (K)

def get_speed_of_sound(h):
    """
    Calculates the speed of sound at a given altitude h (in meters)
    using the ISA temperature model.
    """
    # Layer 0: Troposphere (0 to 11,000 m)
    h_base0 = 0.0
    T_base0 = T0
    a0 = -0.0065 # Lapse rate (K/m)

    # Layer 1: Tropopause (11,000 to 20,000 m)
    h_base1 = 11000.0
    T_base1 = T_base0 + a0 * (h_base1 - h_base0)

    # Layer 2: Stratosphere 1 (20,000 to 32,000 m)
    h_base2 = 20000.0
    T_base2 = T_base1
    a2 = 0.001 # Lapse rate (K/m)

    # Determine temperature based on altitude
    if h < h_base1:
        T = T_base0 + a0 * (h - h_base0)
    elif h < h_base2:
        T = T_base1
    else:
        # Stratosphere 1 (Valid up to 32,000m)
        T = T_base2 + a2 * (h - h_base2)

    # Calculate and return only the speed of sound
    return np.sqrt(gamma * R * T)

