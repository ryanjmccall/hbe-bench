import numpy as np
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. SETUP THE "VIRTUAL FISH"
# ==========================================
n_neurons = 70000
print(f"🧠 Generating {n_neurons} neurons in 3D space...")

# Generate two "hemispheres" using stretched Gaussian distributions
# Left Hemisphere
pos_left = np.random.randn(n_neurons // 2, 3)
pos_left[:, 0] *= 3.0  # Elongate (Anterior-Posterior axis)
pos_left[:, 1] *= 0.8  # Width
pos_left[:, 2] *= 0.6  # Height
pos_left[:, 1] -= 1.0  # Shift Left

# Right Hemisphere
pos_right = np.random.randn(n_neurons // 2, 3)
pos_right[:, 0] *= 3.0
pos_right[:, 1] *= 0.8
pos_right[:, 2] *= 0.6
pos_right[:, 1] += 1.0 # Shift Right

# Combine
positions = np.vstack([pos_left, pos_right])

# ==========================================
# 2. SIMULATE ACTIVITY (THE "LIFE")
# ==========================================
# Generate "firing rates" (some regions hot, some cold)
# We create a "wave" of activity moving through the brain
activity = np.sin(positions[:, 0] * 1.5) + np.cos(positions[:, 1] * 2.0)
activity = (activity - activity.min()) / (activity.max() - activity.min()) # Normalize 0-1

# Add some sparse "bursts" (The 80/20 rule of firing)
burst_mask = np.random.rand(n_neurons) > 0.95
activity[burst_mask] = 1.0

# ==========================================
# 3. RENDER THE POINT CLOUD
# ==========================================
plt.style.use('dark_background')
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot scatter
# c=activity -> Colors by firing rate
# cmap='magma' -> Neon / Cyberpunk heat map
# s=0.2 -> Tiny points for "cloud" effect
scatter = ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], 
                     c=activity, cmap='magma', s=0.1, alpha=0.6)

# Aesthetics (Make it look like a lab instrument)
ax.set_title("ZAPBENCH: 70,000 NEURON EMULATION", color='white', fontsize=14)
ax.set_axis_off() # Hide axes for clean look
ax.view_init(elev=30, azim=45) # Nice angle

# Save
os.makedirs('assets', exist_ok=True)
save_path = 'assets/zapbench_neurons.png'
plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
print(f"✅ Generated Biology Render: {save_path}")

# plt.show()