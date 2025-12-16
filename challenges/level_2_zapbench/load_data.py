import tensorstore as ts
import numpy as np
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm

import os

# FIX: We append '/0' to access the high-res array inside the Zarr group
# ZAPBench Structure: activity.zarr (Group) -> 0 (Array)
BUCKET_PATH = "gs://zapbench-release/volumes/20240930/df_over_f_xyz_chunked/s0"
LOCAL_DATA_PATH = "data/biopsy.npy"

def fetch_brain_slice():
    # Check if data already exists locally
    if os.path.exists(LOCAL_DATA_PATH):
        print(f"   ✅ Found local data at {LOCAL_DATA_PATH}")
        return np.load(LOCAL_DATA_PATH)

    print(f"🧠 Connecting to ZAPBench Cloud...")
    print(f"   Target: {BUCKET_PATH}")
    
    try:
        # Open the remote dataset
        # We specify 'read=True' to ensure it checks existence immediately
        dataset_future = ts.open({
            'driver': 'zarr3',
            'kvstore': BUCKET_PATH
        }, read=True)
        
        dataset = dataset_future.result()
        print(f"   ✅ Connection Successful!")
        print(f"   Shape: {dataset.shape}") # Should be [X, Y, Z, T]
        
        # Download a biopsy (Time: 0-50, Z-slice: 20)
        # New shape is (X, Y, Z, T), so we slice [:, :, 20, 0:50]
        print("   📥 Downloading biopsy (Time:0-50, Z:20)...")
        
        # We download time steps one by one to show progress
        time_steps = 50
        biopsy_frames = []
        
        for t in tqdm(range(time_steps), desc="Downloading frames"):
            # Slice: [X, Y, Z, T] -> [X, Y]
            frame = dataset[:, :, 20, t].read().result()
            biopsy_frames.append(frame)
            
        # Stack frames along time axis -> (T, X, Y)
        biopsy = np.stack(biopsy_frames, axis=0)
        
        # Transpose from (T, X, Y) to (T, Y, X) to match original expectation
        # Note: Previous code expected (X, Y, T) then transposed (2, 1, 0) -> (T, Y, X)
        # Here we have (T, X, Y), so we transpose (0, 2, 1) -> (T, Y, X)
        biopsy = biopsy.transpose(0, 2, 1)
        
        # Save to disk
        os.makedirs(os.path.dirname(LOCAL_DATA_PATH), exist_ok=True)
        np.save(LOCAL_DATA_PATH, biopsy)
        print(f"   💾 Saved data to {LOCAL_DATA_PATH}")
        
        return biopsy

    except Exception as e:
        print(f"\n❌ ERROR: Could not connect to ZAPBench.")
        print(f"   Reason: {str(e)}")
        print("\n--- TROUBLESHOOTING ---")
        print("1. If you have 'gsutil' installed, run this to verify the path:")
        print(f"   gsutil ls -r gs://zapbench-release/volumes/calcium/scan_0/ | head")
        print("2. If it asks for credentials, run:")
        print("   gcloud auth application-default login")
        sys.exit(1)

if __name__ == "__main__":
    brain_data = fetch_brain_slice()
    
    # Visualize
    plt.figure(figsize=(10, 5))
    plt.imshow(brain_data[0], cmap='magma', vmin=0, vmax=200)
    plt.title("ZAPBench Real Data (t=0, z=20)")
    plt.colorbar(label="Calcium Signal")
    output_path = "data/brain_scan.png"
    plt.savefig(output_path)
    print(f"📸 Saved '{output_path}'")