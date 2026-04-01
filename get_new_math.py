import Input_updated as ip_exx

TOTAL_CARGO_MASS = ip_exx.TOTAL_CARGO_MASS
V_front_orig = ip_exx.V_front_orig
V_aft_orig = ip_exx.V_aft_orig
V_front_new = ip_exx.V_front_new
V_aft_new = ip_exx.V_aft_new
V_total_new = ip_exx.V_total_new
W_cargo_fwd = ip_exx.MASS_FRONT_CARGO_EXX
W_cargo_aft = ip_exx.MASS_AFT_CARGO_EXX

payload = ip_exx.W_max_payload
mzfw = ip_exx.MZFW_EXX
fuel = ip_exx.W_fuel

print("--- NEW CARGO MATH ---")
print(f"Total initial cargo mass = {TOTAL_CARGO_MASS:.2f} kg")
print(f"Original V_fwd = {V_front_orig:.3f} m^3, Original V_aft = {V_aft_orig:.3f} m^3")
print(f"New V_fwd = {V_front_new:.3f} m^3, New V_aft = {V_aft_new:.3f} m^3, Total New V = {V_total_new:.3f} m^3")
print(f"New Cargo FWD = {W_cargo_fwd:.2f} kg, AFT = {W_cargo_aft:.2f} kg")
print(f"Total payload = {payload:.2f} kg")
print(f"MZFW = {mzfw:.2f} kg, Fuel = {fuel:.2f} kg")
