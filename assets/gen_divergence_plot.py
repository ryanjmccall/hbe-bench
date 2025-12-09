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
noise_level = 0.5
# Add some "physics noise" but maintain phase
hopf_signal = true_signal + np.random.normal(0, 0.2, size=len(t))

# B. The Transformer (Simulation)
# It's perfect on "Training Data" (History), but fails on "Test Data" (Future)
transformer_signal = true_signal.copy()

# After divergence, it hallucinates (drifts off linearly + random wobbles)
drift_slope = 0.5
for i in range(divergence_point, t_steps):
    # It tries to predict the next step but lacks the 'rho' parameter logic
    # So it slowly drifts away from the attractor manifold
    dt_steps = i - divergence_point
    drift = drift_slope * dt_steps * np.sin(dt_steps * 0.1) # Oscillatory drift
    transformer_signal[i] = true_signal[divergence_point] + drift + np.random.normal(0, 2.0)

# ==========================================
# 3. THE VISUAL (NEON / CYBERPUNK)
# ==========================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))

# Plot lines
ax.plot(t, true_signal, color='#222222', linewidth=6, label='Ground Truth (Physics)', alpha=0.8, zorder=1)
ax.plot(t[:divergence_point], transformer_signal[:divergence_point], color='#FF0055', linewidth=2, zorder=2) # Red (History)
ax.plot(t[divergence_point:], transformer_signal[divergence_point:], color='#FF0055', linewidth=2, linestyle='--', label='Transformer (Simulation)', zorder=2) # Red (Future)
ax.plot(t, hopf_signal, color='#00CCFF', linewidth=2, alpha=0.9, label='Hopf Brain (Emulation)', zorder=3) # Blue

# Add "The Wall" (Divergence Line)
plt.axvline(x=t[divergence_point], color='white', linestyle=':', linewidth=1, alpha=0.5)
plt.text(t[divergence_point] + 0.5, max(true_signal) + 5, "PREDICTION HORIZON\n(Mind Upload Threshold)", color='white', fontsize=10, verticalalignment='bottom')

# Annotations (The Story)
plt.arrow(t[divergence_point] + 5, transformer_signal[divergence_point+100], 0, -5, color='#FF0055', head_width=1, head_length=2)
plt.text(t[divergence_point] + 6, transformer_signal[divergence_point+100] - 10, "Hallucination\n(Statistical Drift)", color='#FF0055', fontsize=11)

plt.arrow(t[divergence_point] + 15, hopf_signal[divergence_point+300], 0, 5, color='#00CCFF', head_width=1, head_length=2)
plt.text(t[divergence_point] + 12, hopf_signal[divergence_point+300] + 7, "Phase Locked\n(Physical Law)", color='#00CCFF', fontsize=11)

# Polish
ax.set_title("HBE-BENCH: SIMULATION VS EMULATION", fontsize=18, fontweight='bold', color='white')
ax.set_xlabel("Time (Lyapunov Units)", color='gray')
ax.set_ylabel("State Space (X)", color='gray')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444444')
ax.spines['left'].set_color('#444444')
ax.legend(loc='lower left', frameon=False, fontsize=10)
plt.grid(color='#222222', linestyle='-', linewidth=0.5)

# Save
os.makedirs('assets', exist_ok=True)
save_path = 'assets/divergence_plot.png'
plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')

# Show (optional, if running in notebook)
# plt.show()
