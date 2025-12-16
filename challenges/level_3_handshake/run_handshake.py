import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

class BiologicalOscillator:
    """
    Simulates the 'Teacher' signal (The Brain).
    Uses a Stuart-Landau oscillator to create a stable limit cycle with some biological noise.
    """
    def __init__(self, omega=0.1, noise_level=0.05):
        self.omega = omega  # Natural frequency
        self.noise_level = noise_level
        self.state = 1.0 + 0.0j # Complex state (z)
    
    def step(self):
        # Hopf bifurcation normal form: dz/dt = (1 - |z|^2)z + i*omega*z
        # This creates a stable circle of radius 1.
        
        # Euler integration step
        dt = 0.1
        z = self.state
        
        # Deterministic dynamics
        dz = (1 - abs(z)**2)*z + 1j * self.omega * z
        
        # Add biological noise
        noise = self.noise_level * (np.random.randn() + 1j * np.random.randn())
        
        self.state = z + dz * dt + noise
        return np.real(self.state)

class BaselineAgent:
    """
    A 'Bronze' level agent. 
    It is a simple 'Leaky Echo'. It doesn't have its own internal oscillator.
    It relies entirely on the input signal to drive it.
    """
    def __init__(self):
        self.val = 0.0
        self.momentum = 0.0
        
    def step(self, input_signal, coupling_strength):
        """
        coupling_strength (alpha): 1.0 = Full Connection, 0.0 = Disconnected
        """
        # If connected, pull towards input. 
        # If disconnected, it has no internal drive (Death).
        if coupling_strength > 0:
            target = input_signal
            self.val = self.val * 0.9 + target * 0.1 # Simple smoothing
        else:
            self.val = self.val * 0.95 # Decay to zero (Death)
            
        return self.val

def calculate_ltv(signal_a, signal_b):
    """
    Calculates the Locking Temporal Variance (LTV).
    LTV = | mean( exp(i * delta_phi) ) |
    """
    # 1. Get analytical signal using Hilbert Transform to find Phase
    analytic_a = hilbert(signal_a)
    analytic_b = hilbert(signal_b)
    
    phase_a = np.angle(analytic_a)
    phase_b = np.angle(analytic_b)
    
    # 2. Calculate Phase Difference
    delta_phi = phase_a - phase_b
    
    # 3. Calculate LTV (Vector Strength)
    # The magnitude of the mean vector. 
    # If phases are locked, vectors align -> magnitude 1.0
    # If phases are random, vectors cancel -> magnitude 0.0
    complex_vectors = np.exp(1j * delta_phi)
    ltv = np.abs(np.mean(complex_vectors))
    
    return ltv, phase_a, phase_b

def run_handshake_protocol():
    print("🤝 Initializing LEVEL 3: THE HANDSHAKE PROTOCOL")
    print("---------------------------------------------")
    
    # 1. Setup
    brain = BiologicalOscillator(omega=0.2)
    agent = BaselineAgent()
    
    duration = 500
    handshake_start = 200
    handshake_end = 300
    
    history_brain = []
    history_agent = []
    alphas = []
    
    print("   [Phase 1] Entrainment (t=0 to t=200)")
    print("   [Phase 2] The Handshake (t=200 to t=300)")
    print("   [Phase 3] Solo Flight (t=300 to t=500)")
    
    # 2. Run Simulation
    for t in range(duration):
        # Calculate Coupling Strength (Alpha)
        if t < handshake_start:
            alpha = 1.0
        elif t > handshake_end:
            alpha = 0.0
        else:
            # Linear ramp down from 1.0 to 0.0
            progress = (t - handshake_start) / (handshake_end - handshake_start)
            alpha = 1.0 - progress
            
        alphas.append(alpha)
        
        # Step Physics
        brain_signal = brain.step()
        agent_signal = agent.step(brain_signal, alpha)
        
        history_brain.append(brain_signal)
        history_agent.append(agent_signal)

    # 3. Analysis
    # We only care about LTV during the "Solo Flight" (Phase 3)
    # Did the agent survive the disconnect?
    solo_brain = history_brain[handshake_end:]
    solo_agent = history_agent[handshake_end:]
    
    ltv_score, _, _ = calculate_ltv(solo_brain, solo_agent)
    
    # 4. Visualization
    plt.figure(figsize=(12, 6))
    
    # Plot signals
    plt.subplot(2, 1, 1)
    plt.plot(history_brain, label='Biological Signal (Teacher)', alpha=0.6, color='green')
    plt.plot(history_agent, label='Digital Agent (Student)', alpha=0.8, color='blue', linestyle='--')
    
    # Plot Handshake Zone
    plt.axvspan(handshake_start, handshake_end, color='yellow', alpha=0.2, label='Handshake Zone')
    plt.axvline(handshake_end, color='red', linestyle=':', label='Disconnect Point')
    
    plt.title(f'The Handshake Test (LTV Score: {ltv_score:.4f})')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # Plot Coupling
    plt.subplot(2, 1, 2)
    plt.plot(alphas, color='orange', label='Coupling Strength (Alpha)')
    plt.xlabel('Time')
    plt.ylabel('Alpha')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show() # In a headless env, this might need plt.savefig()

    # 5. Verdict
    print(f"\n📊 RESULTS")
    print(f"   LTV Score: {ltv_score:.4f}")
    
    if ltv_score > 0.99:
        print("   Status: 🟢 PASS (Immortality Achieved)")
    elif ltv_score > 0.8:
        print("   Status: 🟡 WARNING (Drift Detected)")
    else:
        print("   Status: 🔴 FAIL (Subjective Death)")
        print("   Reason: The agent flattened out after disconnect. It was a mirror, not a mind.")

if __name__ == "__main__":
    run_handshake_protocol()