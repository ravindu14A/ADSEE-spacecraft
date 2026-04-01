"""
Weight Breakdown: Table (LaTeX) for CRJ-EXX
Uses Input_updated.py data.
"""
import Input_updated as ip_exx

mtow            = ip_exx.MTOW
batteries       = ip_exx.TOTAL_BATT_MASS
eow_batt        = ip_exx.EOW  # EOW in updated already includes batteries
oew             = eow_batt - batteries
payload_max     = ip_exx.W_max_payload
fuel_at_max_pay = ip_exx.W_fuel
pax_luggage     = ip_exx.W_pax_luggage
front_cargo     = ip_exx.W_front_cargo
aft_cargo       = ip_exx.W_aft_cargo

print(f"""
\\begin{{table}}[htpb]
    \\centering
    \\caption{{CRJ-EXX Modified Weight Breakdown}}
    \\label{{tab:weight_breakdown_exx}}
    \\renewcommand{{\\arraystretch}}{{1.3}}
    \\begin{{tabular}}{{@{{}}l c c@{{}}}}
        \\toprule
        \\textbf{{Weight Component}} & \\textbf{{Mass [kg]}} & \\textbf{{\\% of MTOW}} \\\\
        \\midrule
        \\textbf{{Maximum Takeoff Weight (MTOW)}} & \\textbf{{{mtow:,.0f}}} & \\textbf{{100.0\\%}} \\\\
        \\midrule
        Operational Empty Weight (OEW base) & {oew:,.0f} & {oew/mtow*100:.1f}\\% \\\\
        Battery System Weight & {batteries:,.0f} & {batteries/mtow*100:.1f}\\% \\\\
        \\quad \\textit{{Total EOW + Batteries}} & \\textit{{{eow_batt:,.0f}}} & \\textit{{{eow_batt/mtow*100:.1f}\\%}} \\\\
        \\midrule
        Fuel Weight (@ Max Payload) & {fuel_at_max_pay:,.0f} & {fuel_at_max_pay/mtow*100:.1f}\\% \\\\
        Maximum Payload Weight & {payload_max:,.0f} & {payload_max/mtow*100:.1f}\\% \\\\
        \\midrule
        \\multicolumn{{3}}{{@{{}}l}}{{\\textit{{Payload Breakdown:}}}} \\\\
        \\quad -- Pax \\& Cabin Luggage (22 rows) & {pax_luggage:,.0f} & {pax_luggage/mtow*100:.1f}\\% \\\\
        \\quad -- Front Cargo Hold & {front_cargo:,.0f} & {front_cargo/mtow*100:.1f}\\% \\\\
        \\quad -- Aft Cargo Hold & {aft_cargo:,.0f} & {aft_cargo/mtow*100:.1f}\\% \\\\
        \\bottomrule
    \\end{{tabular}}
\\end{{table}}
""")
