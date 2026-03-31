"""
Weight Breakdown: Table (LaTeX) + Pie Chart for CRJ-1000 Baseline
Uses Input.py (Task 1) data only.
"""
import Input as ip
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# ── Extract values from Input.py ──
mtow            = ip.MTOW
oew             = ip.EOW
payload_max     = ip.W_max_payload
fuel_at_max_pay = ip.W_fuel
pax_luggage     = ip.W_pax_luggage
front_cargo     = ip.W_front_cargo
aft_cargo       = ip.W_aft_cargo

# ── Print LaTeX table ──
print("="*60)
print("LaTeX Table:")
print("="*60)
print(f"""
\\begin{{table}}[htpb]
    \\centering
    \\caption{{CRJ-1000 Baseline Weight Breakdown}}
    \\label{{tab:weight_breakdown_task1}}
    \\renewcommand{{\\arraystretch}}{{1.3}}
    \\begin{{tabular}}{{@{{}}l c c@{{}}}}
        \\toprule
        \\textbf{{Weight Component}} & \\textbf{{Mass [kg]}} & \\textbf{{\\% of MTOW}} \\\\
        \\midrule
        \\textbf{{Maximum Takeoff Weight (MTOW)}} & \\textbf{{{mtow:,.0f}}} & \\textbf{{100.0\\%}} \\\\
        \\midrule
        Operational Empty Weight (OEW) & {oew:,.0f} & {oew/mtow*100:.1f}\\% \\\\
        Fuel Weight (@ Max Payload) & {fuel_at_max_pay:,.0f} & {fuel_at_max_pay/mtow*100:.1f}\\% \\\\
        Maximum Payload Weight & {payload_max:,.0f} & {payload_max/mtow*100:.1f}\\% \\\\
        \\midrule
        \\multicolumn{{3}}{{@{{}}l}}{{\\textit{{Payload Breakdown:}}}} \\\\
        \\quad -- Pax \\& Cabin Luggage & {pax_luggage:,.0f} & {pax_luggage/mtow*100:.1f}\\% \\\\
        \\quad -- Front Cargo Hold & {front_cargo:,.0f} & {front_cargo/mtow*100:.1f}\\% \\\\
        \\quad -- Aft Cargo Hold & {aft_cargo:,.0f} & {aft_cargo/mtow*100:.1f}\\% \\\\
        \\bottomrule
    \\end{{tabular}}
\\end{{table}}
""")
print("="*60)

# ══════════════════════════════════════════════════════════════
# PIE CHART
# ══════════════════════════════════════════════════════════════
mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 11,
})

labels = [
    'OEW',
    'Fuel (@ max payload)',
    'Pax & cabin luggage',
    'Front cargo hold',
    'Aft cargo hold',
]
sizes  = [oew, fuel_at_max_pay, pax_luggage, front_cargo, aft_cargo]
pcts   = [s / mtow * 100 for s in sizes]

# Premium colour palette
colors = ['#1D3557', '#457B9D', '#2A9D8F', '#E63946', '#F4A261']

fig, ax = plt.subplots(figsize=(9, 6))
fig.patch.set_facecolor('white')

wedges, texts, autotexts = ax.pie(
    sizes,
    colors=colors,
    autopct=lambda p: f'{p:.1f}%' if p > 3 else '',
    pctdistance=0.78,
    startangle=140,
    wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2),
)

for at in autotexts:
    at.set_fontsize(10)
    at.set_fontweight('bold')
    at.set_color('white')

# Legend labels: "Name — 1,234 kg (12.3%)"
legend_labels = [
    f'{lab} — {s:,.0f} kg ({p:.1f}%)'
    for lab, s, p in zip(labels, sizes, pcts)
]

leg = ax.legend(
    wedges, legend_labels,
    title='Weight Components',
    title_fontproperties={'weight': 'bold', 'size': 12},
    loc='center left',
    bbox_to_anchor=(1.02, 0.5),
    fontsize=10,
    frameon=True,
    fancybox=False,
    edgecolor='#CCCCCC',
    framealpha=0.95,
    borderpad=1.0,
    labelspacing=1.0,
)
leg.get_frame().set_linewidth(0.6)

# Centre text inside the donut
ax.text(0, 0, f'MTOW\n{mtow:,.0f} kg',
        ha='center', va='center', fontsize=13, fontweight='bold', color='#333')

ax.set_title('CRJ-1000 Baseline — Weight Breakdown',
             fontweight='bold', fontsize=15, color='#222', pad=18)

plt.tight_layout()
plt.savefig('Weight_Breakdown_Pie.png', dpi=300, facecolor='white', bbox_inches='tight')
print("Saved: Weight_Breakdown_Pie.png")
plt.show()
