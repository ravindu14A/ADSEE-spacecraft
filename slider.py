import tkinter as tk
from tkinter import ttk
import math

def calculate_aerodynamics(event=None):
    """Reads slider values, calculates Raymer equations, and updates the UI."""
    try:
        # 1. Get values from sliders
        A = scale_A.get()
        sweep_deg = scale_sweep.get()
        M = scale_M.get()
        taper = scale_taper.get()
        i_w = scale_iw.get()
        twist = scale_twist.get()
        alpha_0l = -2.5 # Kept static as per our CRJ assumption
        tail_cl = scale_tail.get()
        
        kappa = 0.95
        sweep_rad = math.radians(sweep_deg)
        
        # 2. Raymer's Math
        beta = math.sqrt(1 - M**2)
        
        term1 = (A**2 * beta**2) / (kappa**2)
        term2 = 1 + (math.tan(sweep_rad)**2 / beta**2)
        denominator = 2 + math.sqrt(4 + term1 * term2)
        
        CL_alpha_rad = (2 * math.pi * A) / denominator
        CL_alpha_deg = CL_alpha_rad * (math.pi / 180.0)
        
        twist_factor = (1 + 2 * taper) / (3 + 3 * taper)
        alpha_0L_w_deg = alpha_0l + (twist * twist_factor)
        
        CL0_wing = CL_alpha_deg * (i_w - alpha_0L_w_deg)
        CL0_total = CL0_wing + tail_cl
        
        # 3. Update the Output Labels
        lbl_beta_val.config(text=f"{beta:.4f}")
        lbl_cla_val.config(text=f"{CL_alpha_deg:.4f} per deg")
        lbl_a0l_val.config(text=f"{alpha_0L_w_deg:.4f} deg")
        lbl_wing_val.config(text=f"{CL0_wing:.4f}")
        lbl_total_val.config(text=f"{CL0_total:.4f}")
        
    except ValueError:
        pass # Ignore errors during startup before all variables initialize

# ==========================================
# GUI SETUP
# ==========================================
root = tk.Tk()
root.title("Raymer's CL0 Component Buildup Calculator")
root.geometry("700x500")
root.configure(padx=20, pady=20)

# Create Left (Controls) and Right (Results) Frames
frame_controls = tk.LabelFrame(root, text="Aircraft Geometry (Inputs)", padx=15, pady=15)
frame_controls.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

frame_results = tk.LabelFrame(root, text="Aerodynamic Results (Raymer)", padx=15, pady=15)
frame_results.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

# --- SLIDERS (Left Frame) ---
def create_slider(parent, label, from_, to, resolution, default):
    tk.Label(parent, text=label, font=("Arial", 10, "bold")).pack(anchor="w")
    scale = tk.Scale(parent, from_=from_, to=to, resolution=resolution, orient=tk.HORIZONTAL, length=250, command=calculate_aerodynamics)
    scale.set(default)
    scale.pack(anchor="w", pady=(0, 10))
    return scale

scale_M     = create_slider(frame_controls, "Cruise Mach Number", 0.3, 0.9, 0.01, 0.78)
scale_A     = create_slider(frame_controls, "Aspect Ratio (A)", 5.0, 12.0, 0.1, 8.85)
scale_sweep = create_slider(frame_controls, "Sweep (Half-Chord) [deg]", 0, 45, 1, 22)
scale_taper = create_slider(frame_controls, "Taper Ratio", 0.1, 1.0, 0.01, 0.28)
scale_iw    = create_slider(frame_controls, "Wing Incidence [deg]", 0.0, 5.0, 0.1, 1.5)
scale_twist = create_slider(frame_controls, "Tip Washout Twist [deg]", -5.0, 0.0, 0.1, -3.0)
scale_tail  = create_slider(frame_controls, "Tail Trim Downforce (CL)", -0.15, 0.0, 0.01, -0.06)

# --- RESULTS DASHBOARD (Right Frame) ---
def create_result_row(parent, label_text, is_bold=False):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.X, pady=10)
    font_style = ("Arial", 12, "bold") if is_bold else ("Arial", 11)
    
    lbl_title = tk.Label(frame, text=label_text, font=font_style, fg="#333333")
    lbl_title.pack(side=tk.LEFT)
    
    lbl_val = tk.Label(frame, text="0.0000", font=("Courier", 12, "bold"), fg="#0052cc" if not is_bold else "#cc0000")
    lbl_val.pack(side=tk.RIGHT)
    return lbl_val

lbl_beta_val = create_result_row(frame_results, "1. Compressibility (Beta):")
lbl_cla_val  = create_result_row(frame_results, "2. 3D Lift Curve Slope:")
lbl_a0l_val  = create_result_row(frame_results, "3. 3D Wing Zero-Lift Angle:")
lbl_wing_val = create_result_row(frame_results, "4. Isolated Wing CL0:")

# Separator line
ttk.Separator(frame_results, orient='horizontal').pack(fill='x', pady=20)

# Final Total Callout
lbl_total_val = create_result_row(frame_results, "TOTAL AIRCRAFT CL0:", is_bold=True)

# Initialize calculations with default values on startup
calculate_aerodynamics()

# Run the application
root.mainloop()