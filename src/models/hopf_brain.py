import torch
import torch.nn as nn
import torch.nn.functional as F
import sys
import numpy as np

# --- DEPENDENCY CHECK ---
try:
    from torchdiffeq import odeint
except ImportError:
    print("⚠️ Missing Dependency: torchdiffeq")
    print("Please run: !pip install torchdiffeq")
    sys.exit(1)

# ==============================================================================
# 1. THE DYNAMIC GEOMETRY (The "Rubber Sheet" Physics)
# ==============================================================================
class DynamicHopfManifold:
    """
    Implements a Riemannian Manifold with a Variable Metric Tensor.
    
    Biological Equivalent: 
    - Base State: Theta Frequency = 8Hz (Standard Grid Scale)
    - Stressed State: Theta Frequency < 8Hz (Expanded Grid Scale via ACh)
    """
    
    @staticmethod
    def project_to_sphere(z, radius=1.0):
        """
        Maps Euclidean vectors to a sphere of variable radius.
        Radius = 1.0 represents the 'Familiar' environment.
        Radius > 1.0 represents the 'Expanded' (Novel) grid.
        """
        norm = z.norm(dim=-1, keepdim=True) + 1e-6
        return (z / norm) * radius

    @staticmethod
    def project_to_tangent(z, v):
        """
        Projects velocity 'v' onto the tangent space of the sphere at 'z'.
        Ensures the flow stays ON the surface, regardless of the current radius.
        """
        z_unit = z / (z.norm(dim=-1, keepdim=True) + 1e-6)
        dot = (v * z_unit).sum(dim=-1, keepdim=True)
        return v - dot * z_unit

    @staticmethod
    def modulate_metric(stress_signal):
        """
        Converts a 'Novelty Signal' (Prediction Error) into a Geometric Scaling Factor.
        
        Ref: Barry et al. (2012) - Novelty expands grid scale.
        Math: Scale ~ 1 + alpha * Stress
        """
        # Sigmoid to bound the expansion (e.g., max 1.5x expansion)
        expansion_factor = 1.0 + 0.5 * torch.sigmoid(stress_signal)
        return expansion_factor

# ==============================================================================
# 2. THE DYNAMICS ENGINE (The "Brain")
# ==============================================================================
class VectorFieldNet(nn.Module):
    """
    Predicts velocity v_t(z) given State (z), Time (t), and Novelty (stress).
    """
    def __init__(self, dim=4, hidden_dim=128):
        super().__init__()
        # Input: State (dim) + Time (1) + Stress (1)
        self.net = nn.Sequential(
            nn.Linear(dim + 2, hidden_dim), 
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, dim)
        )
    
    def forward(self, t, z, stress):
        # 1. Align inputs
        if t.dim() == 0: t = t.expand(z.shape[0], 1)
        if stress.dim() == 0: stress = stress.expand(z.shape[0], 1)
        
        inp = torch.cat([z, t, stress], dim=-1)
        
        # 2. Predict Raw Velocity
        v_raw = self.net(inp)
        
        # 3. ENFORCE TOPOLOGY
        # Project onto the tangent of the CURRENT (possibly expanded) sphere
        v_constrained = DynamicHopfManifold.project_to_tangent(z, v_raw)
        return v_constrained

class HopfFlowMatcher(nn.Module):
    def __init__(self, input_dim=70000, latent_dim=4):
        super().__init__()
        self.encoder = nn.Linear(input_dim, latent_dim)
        self.vector_field = VectorFieldNet(dim=latent_dim)
        self.decoder = nn.Linear(latent_dim, input_dim)
        self.latent_dim = latent_dim
    
    def encode(self, x, stress=None):
        """
        Encodes data to latent space, adjusting the 'Ruler' based on stress.
        """
        z_raw = self.encoder(x)
        
        # Determine the Scale (Metric Tensor)
        if stress is None:
            # Default to baseline (radius=1.0) if no stress signal provided
            radius = 1.0
        else:
            radius = DynamicHopfManifold.modulate_metric(stress)
            
        return DynamicHopfManifold.project_to_sphere(z_raw, radius)
        
    def forward(self, x_current, t_span, stress=None):
        """
        Simulates the future dynamics.
        """
        # 1. Encode with Dynamic Metric
        z0 = self.encode(x_current, stress)
        
        # 2. Define the ODE function (closure for torchdiffeq)
        # The solver needs a function func(t, y) -> dy/dt
        def ode_func(t, z):
            # For inference, we assume stress is constant over the integration step
            # or decays. Here we hold it constant for simplicity.
            current_stress = stress if stress is not None else torch.zeros(z.shape[0], 1).to(z.device)
            return self.vector_field(t, z, current_stress)
        
        # 3. Integrate on the Manifold
        z_traj = odeint(ode_func, z0, t_span)
        
        # 4. Decode
        x_pred = self.decoder(z_traj)
        return x_pred

# ==============================================================================
# 3. THE "NOVELTY" TRAINING LOOP
# ==============================================================================
def train_step(model, x_0, x_1, optimizer):
    optimizer.zero_grad()
    
    # 1. Calculate "Biological Novelty" (Prediction Error proxy)
    # In a real loop, this would be the error from the PREVIOUS step.
    # Here we simulate it as the distance between frames.
    novelty_signal = (x_1 - x_0).norm(dim=-1, keepdim=True) # Simple proxy
    novelty_signal = torch.log1p(novelty_signal) # Log-scale for stability
    
    # 2. Project to Dynamic Manifold
    # The 'Ruler' stretches based on how surprising the data is.
    z_0 = model.encode(x_0, stress=novelty_signal)
    z_1 = model.encode(x_1, stress=novelty_signal) # Target is also on the expanded grid
    
    # 3. Sample Time
    t = torch.rand(z_0.shape[0], 1)
    
    # 4. Compute Geodesic Target (on the expanded sphere)
    # Linear interp + Dynamic Projection
    radius = DynamicHopfManifold.modulate_metric(novelty_signal)
    z_t_raw = (1 - t) * z_0 + t * z_1
    z_t = DynamicHopfManifold.project_to_sphere(z_t_raw, radius)
    
    v_target_raw = z_1 - z_0
    v_target = DynamicHopfManifold.project_to_tangent(z_t, v_target_raw)
    
    # 5. Predict Flow
    v_pred = model.vector_field(t, z_t, novelty_signal)
    
    # 6. Loss
    loss = torch.mean((v_pred - v_target) ** 2)
    
    loss.backward()
    optimizer.step()
    return loss.item()

# ==============================================================================
# 4. EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("Initializing The Hopf Brain V2 (Dynamic Metric Tensor)...")
    
    BATCH_SIZE = 16
    NEURONS = 70000
    LATENT_DIM = 4 
    
    model = HopfFlowMatcher(input_dim=NEURONS, latent_dim=LATENT_DIM)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Mock Data
    x_t0 = torch.randn(BATCH_SIZE, NEURONS) 
    x_t1 = torch.randn(BATCH_SIZE, NEURONS) 
    
    loss = train_step(model, x_t0, x_t1, optimizer)
    
    print(f"Training Step Complete. Loss: {loss:.6f}")
    print("Status: Metric Tensor Modulated by Novelty Signal.")