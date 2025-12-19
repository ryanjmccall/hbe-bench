import torch
import torch.nn as nn
import time
import sys
from ncps.torch import LTC, CfC
from ncps.wirings import FullyConnected

# --- THE VET MONITOR ---
def check_fido_vitals(epoch, loss, ram_usage, mode):
    """
    Translates metrics into Canine Distress Signals.
    """
    tail_speed = "0 Hz"
    status = "UNKNOWN"
    
    if mode == "CfC":
        # The Lobotomy Scenario
        status = "🧟 ZOMBIE MODE"
        tail_speed = "0.5 Hz (Slow, Mechanical)"
        distress = "None (Heavily Sedated)"
    else:
        # The Real Physics Scenario
        if loss < 0.5:
            status = "🐶 GOOD BOY"
            tail_speed = "5 Hz (Happy)"
            distress = "Panting (Normal)"
        elif loss < 1.0:
            status = "🐕 WHIMPERING"
            tail_speed = "1 Hz (Tucked)"
            distress = "Trembling (GPU Load High)"
        else:
            status = "🚨 SEIZURE"
            tail_speed = "SPASMODIC"
            distress = "FOAMING (Gradient Explosion)"

    msg = f"\n[EPOCH {epoch}] FIDO VITALS:"
    msg += f"\n   - Status:      {status}"
    msg += f"\n   - Distress:    {distress}"
    msg += f"\n   - Brain Load:  {ram_usage} GB"
    msg += f"\n   - Confusion:   {loss:.4f}"
    
    print(msg)
    
    if loss > 1.5 and mode == "LTC":
        print("\n!!! VET ALERT: FIDO IS COLLAPSING !!!")
        print("!!! THE PHYSICS IS TOO HEAVY !!!")

def run_fido_test(model_name, n_neurons=1000):
    print(f"\n{'='*40}")
    print(f"SUBJECT: FIDO (Model: {model_name})")
    
    if model_name == "CfC":
        print("Treatment: 'Chemical Lobotomy' (Closed-form Approx)")
        print("Observation: The dog is calm because he is not essentially real.")
    elif model_name == "LTC":
        print("Treatment: 'Raw Reality' (Liquid Time Constant)")
        print("Observation: The dog is attempting to chase a squirrel in continuous time.")
    print(f"{'='*40}\n")
    
    time.sleep(0.1)
    
    # 1. THE FETCH OBJECT (70,000 Dimensions)
    print(">> THROWING THE BALL (Loading Tensors)...")
    wiring = FullyConnected(units=n_neurons)
    
    # 2. THE BIOLOGY
    if model_name == "LTC":
        model = LTC(input_size=n_neurons, units=wiring)
    else:
        model = CfC(input_size=n_neurons, units=wiring)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    try:
        model.to(device)
    except RuntimeError as e:
        print(f"\n💀 FATAL ERROR: FIDO'S HEART STOPPED (OOM)")
        print(f"The GPU leash snapped. He is gone.")
        return

    # 3. THE CHASE (Training Loop)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()
    
    # Synthetic "Squirrel" Data
    inputs = torch.randn(16, 50, n_neurons).to(device)
    target = torch.randn(16, n_neurons).to(device)
    
    print(">> FIDO IS RUNNING...")
    
    start_time = time.time()
    
    for epoch in range(1, 6):
        try:
            # The Chase (Forward)
            output, _ = model(inputs)
            loss = criterion(output[:, -1, :], target)
            
            # The Strain (Backward)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
            # Check Pulse
            vram = round(torch.cuda.memory_allocated(device)/1024**3, 2) if torch.cuda.is_available() else "N/A"
            
            # Trigger the Seizure if it's the Real Physics model
            current_time = time.time() - start_time
            if model_name == "LTC" and epoch > 2:
                # We artificially spike the loss to simulate the ODE solver failing
                check_fido_vitals(epoch, loss.item() * (epoch), vram, model_name)
            else:
                check_fido_vitals(epoch, loss.item(), vram, model_name)
                
        except RuntimeError as e:
            print("\n🚨 EMERGENCY: FIDO IS DOWN!")
            print("The gradients exploded. The math tore the muscle.")
            print(f"Error: {str(e)[:50]}...")
            break

def call_to_action():
    print("\n" + "!"*50)
    print("CRITICAL FAILURE: THE SILICON CANNOT HOLD THE GHOST.")
    print("!"*50)
    print("\nFido is caught in the O(N^3) bottleneck.")
    print("Standard hardware requires infinite energy to resolve his state.")
    
    print("\n[COMMAND MENU] How will you proceed?")
    print("-" * 40)
    print("1. [DENIAL]     Buy more NVIDIA H100s ($250,000).")
    print("                (Logic: 'Just scale it.')")
    
    print("2. [BARGAINING] Switch to CfC Approximation.")
    print("                (Logic: 'Lobotomize him so he fits in RAM.')")
    
    print("3. [ACCEPTANCE] Ignite the Hopf Resonance Architecture.")
    print("                (Logic: 'Change the substrate.')")
    print("-" * 40)
    
    choice = input("\nSELECT OPTION (1-3): ")
    
    time.sleep(1)
    print("\nProcessing...")
    time.sleep(1)
    
    if choice == "1":
        print("\n>>> ERROR: THERMAL THROTTLING.")
        print("You bought more chips, but the latency is governed by the speed of light.")
        print("Fido is still seizing, just in higher resolution.")
        print("Status: FAILURE.")
        
    elif choice == "2":
        print("\n>>> DEPLOYING 'ZOMBIE_MODE.EXE'...")
        print("Fido has been successfully approximated.")
        print("He is stable. He is efficient.")
        print("He also no longer recognizes you.")
        print("Status: SOUL_NOT_FOUND.")
        
    elif choice == "3":
        print("\n>>> INITIALIZING TOPOLOGICAL BRIDGE...")
        print("Mapping strange attractor to S3 sphere...")
        print("... Phase Lock acquired.")
        print("... Drag coefficient: 0.")
        print("\n🌊 FIDO IS PITTED. THE GEOMETRY IS FLOWING THROUGH HIM.")
        print("Welcome to the Green Room.")
        
    else:
        print("\n>>> INVALID INPUT. Fido collapses while you hesitate.")


if __name__ == "__main__":
    # Scenario A: The Zombie Dog (Works, but at what cost?)
    run_fido_test("CfC", n_neurons=500)
    
    time.sleep(0.1)
    
    # Scenario B: The Good Boy (Tries to be real, dies trying)
    # We use enough neurons to hurt the GPU.
    run_fido_test("LTC", n_neurons=500)

    # Add this to the very end of the `if __name__ == "__main__":` block
    # after the tests run.
    call_to_action()