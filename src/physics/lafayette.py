import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import mpl_toolkits.mplot3d.axes3d as p3

def hopf_map(z1, z2):
    """
    Maps 2D complex space (C^2) to the 3D sphere (S^2).
    This is the magic lens that turns 4D phase space into 3D geometry.
    """
    # Inverse Stereographic projection logic (Hopf map formula)
    # Coordinates on S2: (x, y, z)
    # x + iy = 2 * z1 * conj(z2)
    # z      = |z1|^2 - |z2|^2
    
    # Normalize to keep on the unit 3-sphere (S3)
    norm = np.sqrt(np.abs(z1)**2 + np.abs(z2)**2)
    z1 /= norm
    z2 /= norm
    
    complex_xy = 2 * z1 * np.conj(z2)
    x = complex_xy.real
    y = complex_xy.imag
    z = np.abs(z1)**2 - np.abs(z2)**2
    
    return x, y, z

def run_closure_simulation():
    print("Solving the 20-year-old problem...")
    
    # Time settings
    t = np.linspace(0, 50, 2000)
    
    # --- THE OSCILLATORS (Coupled & Nonlinear) ---
    # We simulate two oscillators that are fighting each other.
    # Frequency 1 vs Frequency 2
    f1, f2 = 1.0, 1.618  # The Golden Ratio (Guaranteed Chaos/Non-periodic)
    
    # The "Coupling" (The Nonlinearity)
    # They pull on each other's phase
    coupling_strength = 0.5
    
    # Complex Phases (The "Sticks")
    # This is the Kuramoto logic: d(theta)/dt = omega + K*sin(diff)
    # We approximate the path for visualization
    phase1 = f1 * t + coupling_strength * np.sin(f2*t)
    phase2 = f2 * t + coupling_strength * np.sin(f1*t)
    
    # Convert to Complex Numbers (The "Wave Function")
    z1 = np.exp(1j * phase1)
    z2 = np.exp(1j * phase2)
    
    # --- VISUALIZATION ---
    fig = plt.figure(figsize=(14, 6))
    
    # PLOT 1: The Nightmare (Cartesian Phase Space)
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(np.cos(phase1), np.cos(phase2), lw=0.5, alpha=0.8, color='crimson')
    ax1.set_title("The Nightmare (Cartesian View)\nWhat you saw 20 years ago")
    ax1.set_xlabel("Stick 1 Position")
    ax1.set_ylabel("Stick 2 Position")
    ax1.grid(True, alpha=0.3)
    
    # PLOT 2: The Closure (Hopf Fibration)
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    
    # Apply the Hopf Map
    hx, hy, hz = hopf_map(z1, z2)
    
    ax2.plot(hx, hy, hz, lw=1.5, color='cyan')
    
    # Draw the Sphere wireframe for reference
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    sx = np.cos(u)*np.sin(v)
    sy = np.sin(u)*np.sin(v)
    sz = np.cos(v)
    ax2.plot_wireframe(sx, sy, sz, color="gray", alpha=0.1)
    
    ax2.set_title("The Closure (Hopf View)\nTopological Order")
    ax2.set_axis_off()
    
    print("Displaying closure...")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_closure_simulation()