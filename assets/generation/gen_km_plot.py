import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import os

# ==========================================
# 1. THE PHYSICS (TRUTH)
# ==========================================
def lorenz_system(state, t, sigma=10, rho=28, beta=8/3):
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]

# Time setup
dt = 0.05
t_steps = 1000
t = np.linspace(0, t_steps * dt, t_steps)

# Generate Ground Truth (The Chaos)
initial_state = [1.0, 1.0, 1.0]
trajectory = odeint(lorenz_system, initial_state, t)
true_signal = trajectory[:, 0] # Just plot the X-dimension

# ==========================================
# 2. THE COMPETITORS (SIMULATION VS EMULATION)
# ==========================================
divergence_point = 400 # Where history ends and "Future" begins

# A. The Hopf Brain (Emulation)
# It tracks the truth but with minor sensor noise. It understands the attractor.
hopf_signal = true_signal.copy()
# Add some "physics noise" but maintain phase
np.random.seed(42)
hopf_signal = true_signal + np.random.normal(0, 0.5, size=len(t))

# B. The Transformer (Simulation)
# It's perfect on "Training Data" (History), but fails on "Test Data" (Future)
transformer_signal = true_signal.copy()

# After divergence, it hallucinates (drifts off linearly + random wobbles)
drift_slope = 1.2
for i in range(divergence_point, t_steps):
    # It tries to predict the next step but lacks the 'rho' parameter logic
    dt_steps = i - divergence_point
    # Create a growing sine wave drift (Hallucination)
    drift = drift_slope * (dt_steps * 0.05) * np.sin(dt_steps * 0.2) 
    # Add cumulative error
    transformer_signal[i] = true_signal[divergence_point] + drift + np.random.normal(0, 2.0)

# ==========================================
# 3. THE VISUAL (NEON / CYBERPUNK)
# ==========================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))

# Helper function for glow effect
def plot_glowing_line(x, y, color, label=None, alpha_base=1.0, linewidth_base=2, glow_factor=5):
    # Core line
    ax.plot(x, y, color=color, linewidth=linewidth_base, alpha=alpha_base, label=label, zorder=10)
    # Glow layers
    for i in range(1, glow_factor + 1):
        ax.plot(x, y, color=color, linewidth=linewidth_base + (i * 1.5), alpha=0.15 / i, zorder=10-i)

# 1. Ground Truth (Subtle background trace if needed, but we focus on the signals)

# 2. Transformer (History - Red)
plot_glowing_line(t[:divergence_point], transformer_signal[:divergence_point], 
                  color='#FF0055', linewidth_base=2) 

# 3. Transformer (Future - Red Dashed)
# Dashed core with a faint solid glow to create the "haze" of hallucination
ax.plot(t[divergence_point:], transformer_signal[divergence_point:], 
        color='#FF0055', linewidth=2, linestyle='--', label='Transformer (Simulation)', zorder=10)
ax.fill_between(t[divergence_point:], transformer_signal[divergence_point:] - 5, transformer_signal[divergence_point:] + 5, 
                color='#FF0055', alpha=0.1)

# 4. Hopf Brain (Blue)
plot_glowing_line(t, hopf_signal, color='#00CCFF', label='Hopf Brain (Emulation)', linewidth_base=2)

# Add "The Wall" (Divergence Line)
plt.axvline(x=t[divergence_point], color='white', linestyle=':', linewidth=1, alpha=0.8)
plt.text(t[divergence_point] + 0.5, 250, "PREDICTION HORIZON\n(Mind Upload Threshold)", 
         color='white', fontsize=12, fontweight='bold', verticalalignment='top')

# Annotations (The Story)
# Hallucination Label
hallucination_idx = divergence_point + 150
plt.annotate("Hallucination\n(Statistical Drift)", 
             xy=(t[hallucination_idx], transformer_signal[hallucination_idx]), 
             xytext=(t[hallucination_idx] + 5, transformer_signal[hallucination_idx] - 60),
             arrowprops=dict(arrowstyle='->', color='#FF0055', lw=2),
             color='#FF0055', fontsize=12, fontweight='bold', ha='left')

# Phase Locked Label
phase_idx = divergence_point + 300
plt.annotate("Phase Locked\n(Physical Law)", 
             xy=(t[phase_idx], hopf_signal[phase_idx]), 
             xytext=(t[phase_idx] + 2, hopf_signal[phase_idx] + 60),
             arrowprops=dict(arrowstyle='->', color='#00CCFF', lw=2),
             color='#00CCFF', fontsize=12, fontweight='bold', ha='left')

# Polish
ax.set_title("HBE-BENCH: SIMULATION VS EMULATION", fontsize=20, fontweight='bold', color='white', pad=20)
ax.set_xlabel("Time (Lyapunov Units)", color='gray', fontsize=12)
ax.set_ylabel("State Space (X)", color='gray', fontsize=12)

# Custom Grid
ax.grid(color='#222222', linestyle='-', linewidth=1, alpha=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444444')
ax.spines['left'].set_color('#444444')

# Legend
leg = ax.legend(loc='lower right', frameon=True, fontsize=10, facecolor='black', edgecolor='#444444')
for text in leg.get_texts():
    text.set_color("white")

# Save
os.makedirs('assets', exist_ok=True)
save_path = 'assets/km_plot.png'
plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
# plt.show()