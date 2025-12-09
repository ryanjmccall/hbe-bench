import argparse
import yaml
import torch
from torch.utils.data import DataLoader
from src.data.lorenz_loader import Lorenz96Dataset

# ==========================================
# FACTORY: Selects the Right Phase
# ==========================================
def get_dataset(config):
    phase = config['experiment']['phase']
    
    if phase == "lorenz":
        return Lorenz96Dataset(config['data'])
    elif phase == "ks":
        # return KSEquationDataset(config['data']) # Future Phase 2
        raise NotImplementedError("Phase 2 (KS) not yet implemented")
    elif phase == "zapbench":
        # return ZapBenchDataset(config['data'])   # Future Phase 3
        raise NotImplementedError("Phase 3 (ZapBench) not yet implemented")
    else:
        raise ValueError(f"Unknown phase: {phase}")

# ==========================================
# MAIN LOOP
# ==========================================
def train(config_path):
    # 1. Load Config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    print(f"🚀 Starting Experiment: {config['experiment']['name']}")
    
    # 2. Setup Data
    dataset = get_dataset(config)
    dataloader = DataLoader(dataset, batch_size=config['training']['batch_size'], shuffle=True)
    
    # 3. Setup Model (Placeholder for the Hopf Brain)
    # model = HopfResNet(config) 
    print(f"🧠 Model initialized on {config['training']['device']}")
    
    # 4. Training Loop (Scaffold)
    print(f"🔄 Training on {len(dataset)} samples for {config['training']['epochs']} epochs...")
    
    for epoch in range(config['training']['epochs']):
        # Simulation of a training step
        # batch = next(iter(dataloader))
        # loss = model(batch)
        print(f"   [Epoch {epoch+1}] Loss: 0.XXXX (Simulated)")

    print("✅ Training Complete. Snapshot saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to config yaml")
    args = parser.parse_args()
    
    train(args.config)