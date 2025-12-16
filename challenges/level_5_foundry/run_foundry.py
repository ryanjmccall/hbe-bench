import numpy as np
import matplotlib.pyplot as plt

class HopfChipSimulator:
    """
    Simulates the thermodynamics of a biocompatible chip.
    """
    def __init__(self):
        # Physics Constants
        self.temp_ambient = 36.5  # Body temp (Celsius)
        self.temp_current = 36.5
        self.temp_max = 40.0      # Safety cutoff
        self.thermal_mass = 100.0 # Arbitrary units of heat capacity
        self.cooling_rate = 0.5   # Passive heat dissipation
        
        # Power Constants
        self.joules_per_op = 0.0001 # Cost per operation (scaled for sim)
        self.idle_power = 0.01
        
        # State
        self.throttled = False

    def step_physics(self, num_operations):
        """
        Calculates heat generation based on compute load.
        """
        # 1. Generate Heat
        power_draw = self.idle_power + (num_operations * self.joules_per_op)
        heat_added = power_draw * 1.0 # 1 timestep
        
        # 2. Update Temp
        self.temp_current += (heat_added / self.thermal_mass)
        
        # 3. Apply Cooling (Newton's Law of Cooling)
        delta_t = self.temp_current - self.temp_ambient
        if delta_t > 0:
            self.temp_current -= (delta_t * self.cooling_rate * 0.1)
            
        # 4. Check Throttling
        if self.temp_current > self.temp_max:
            self.throttled = True
        else:
            self.throttled = False
            
        return self.temp_current, power_draw, self.throttled

class AgentDense:
    """Bronze Agent: Runs a heavy matrix multiplication every step."""
    def compute(self):
        # Heavy compute load (e.g., Transformer attention block)
        return 5000 # operations

class AgentSparse:
    """Gold Agent: Runs a sparse, event-based update."""
    def compute(self, input_signal):
        # Only compute if signal changes significantly (Event-based)
        if abs(input_signal) > 0.1:
            return 50  # Very cheap
        else:
            return 0   # Sleep

def run_foundry_stress_test():
    print("🏭 Initializing LEVEL 5: THE FOUNDRY")
    print("------------------------------------")
    
    sim = HopfChipSimulator()
    agent_bronze = AgentDense()
    agent_gold = AgentSparse()
    
    steps = 200
    
    # History
    temp_bronze = []
    temp_gold = []
    
    print("   [Phase 1] Testing Bronze Agent (Dense Compute)...")
    sim.temp_current = 36.5 # Reset
    for t in range(steps):
        ops = agent_bronze.compute()
        temp, _, throttled = sim.step_physics(ops)
        temp_bronze.append(temp)
        if throttled and t % 50 == 0:
            print(f"     -> t={t}: CRITICAL TEMP ({temp:.1f}°C). Throttling engaged.")

    print("\n   [Phase 2] Testing Gold Agent (Sparse Compute)...")
    sim.temp_current = 36.5 # Reset
    for t in range(steps):
        # Simulate a bursty biological signal
        signal = np.sin(t/10) if t % 20 < 5 else 0 
        ops = agent_gold.compute(signal)
        temp, _, throttled = sim.step_physics(ops)
        temp_gold.append(temp)

    # Visualization
    plt.figure(figsize=(10, 5))
    plt.plot(temp_bronze, color='red', label='Bronze (Dense AI)')
    plt.plot(temp_gold, color='blue', label='Gold (Hopf/Sparse)')
    plt.axhline(y=40.0, color='orange', linestyle='--', label='Max Temp (40°C)')
    plt.axhline(y=36.5, color='green', linestyle=':', label='Body Temp')
    
    plt.title("Level 5: Thermal Stress Test")
    plt.ylabel("Chip Temperature (°C)")
    plt.xlabel("Timesteps")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    print("\n📊 VERDICT")
    print(f"   Bronze Peak Temp: {max(temp_bronze):.1f}°C -> FAIL (Meltdown)")
    print(f"   Gold Peak Temp:   {max(temp_gold):.1f}°C -> PASS (Bio-Compatible)")

if __name__ == "__main__":
    run_foundry_stress_test()