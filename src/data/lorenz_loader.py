import numpy as np
import torch
from torch.utils.data import Dataset
from scipy.integrate import odeint
import matplotlib.pyplot as plt

class Lorenz96Dataset(Dataset):
    """
    Phase 1: The Unit Test
    Generates synthetic chaotic data from the Lorenz 96 equations.
    """
    def __init__(self, config, mode='train'):
        self.config = config
        self.mode = mode
        
        # Physics Parameters (Lorenz 96 standard)
        self.F = config.get('forcing', 8.0)  # F=8 causes chaos
        self.N = config.get('num_vars', 40)  # Number of dimensions (variables)
        self.dt = config.get('dt', 0.01)
        self.seq_len = config.get('seq_len', 1000)
        self.history_len = config.get('history_len', 50)
        self.pred_len = config.get('pred_len', 10)
        
        # Generate Data deterministically
        self.data = self._generate_data()
        
    def _lorenz96(self, x, t):
        """
        dx[i]/dt = (x[i+1] - x[i-2]) * x[i-1] - x[i] + F
        """
        # Circular boundary conditions
        N = self.N
        dxdt = np.zeros(N)
        for i in range(N):
            dxdt[i] = (x[(i + 1) % N] - x[(i - 2) % N]) * x[(i - 1) % N] - x[i] + self.F
        return dxdt

    def _generate_data(self):
        print(f"🌀 Generating Lorenz 96 Chaos (F={self.F}, N={self.N})...")
        
        # Deterministic seed for the "Snapshot" philosophy
        np.random.seed(self.config.get('seed', 42))
        
        # Random initial conditions + minimal perturbation
        x0 = self.F * np.ones(self.N)
        x0[0] += 0.01  # Small perturbation to trigger chaos
        
        # Time integration
        t = np.arange(0.0, self.seq_len * self.dt, self.dt)
        x = odeint(self._lorenz96, x0, t)
        
        # Normalize (Standard practice for ML stability)
        mean = x.mean()
        std = x.std()
        x = (x - mean) / std
        
        # Convert to Tensor
        return torch.from_numpy(x).float()

    def __len__(self):
        return len(self.data) - self.history_len - self.pred_len

    def __getitem__(self, idx):
        # Input: History window
        x = self.data[idx : idx + self.history_len]
        # Target: Future window
        y = self.data[idx + self.history_len : idx + self.history_len + self.pred_len]
        return x, y

# ==========================================
# UNIT TEST EXECUTION
# ==========================================
if __name__ == "__main__":
    # Scaffolding Test: Run this file directly to verify Phase 1 works.
    print("🔬 Running Phase 1 Unit Test...")
    
    mock_config = {
        'forcing': 8.0,
        'num_vars': 40,
        'seq_len': 2000,
        'history_len': 50,
        'pred_len': 10,
        'seed': 42
    }
    
    dataset = Lorenz96Dataset(mock_config)
    x, y = dataset[0]
    
    print(f"✅ Dataset Created Successfully")
    print(f"Input Shape (History): {x.shape}")
    print(f"Target Shape (Future): {y.shape}")
    
    # Visual Sanity Check
    plt.figure(figsize=(10, 4))
    plt.plot(dataset.data[:500, 0], label="Dimension 0")
    plt.plot(dataset.data[:500, 1], label="Dimension 1", alpha=0.7)
    plt.title("Lorenz 96 Chaos (First 2 Dimensions)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    print("📊 Plot generated. If you see chaotic waves, the physics is working.")