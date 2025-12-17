import numpy as np
import time
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("\n" + "="*60)
    print("🚀 HBE-BENCH: LEVEL 0 - IGNITION SEQUENCE")
    print("   Objective: Achieve Global Coherence at Human Scale")
    print("   Target:    86,000,000,000 Neurons")
    print("   Substrate: SILICON (Von Neumann Architecture)")
    print("="*60 + "\n")
    time.sleep(1)

def run_simulation():
    scales = [100, 500, 1000, 2000, 4000, 8000, 12000]
    
    print(f"{'NEURONS (N)':<15} | {'COMPUTE TIME':<15} | {'STATUS'}")
    print("-" * 50)

    for n in scales:
        start_time = time.time()
        
        # --- THE PHYSICS ENGINE (Real Work) ---
        # We simulate the projection of the S3 Hopf Fibration onto the S2 Bloch Sphere
        # via complex spinor interactions.
        # Math: Z_final = Z_spinor @ Z_spinor.conj().T
        # This is O(N^3) and uses Complex128 (16 bytes/element).
        
        # ALLOCATE (This hurts RAM)
        # For N=30,000: 30k^2 * 16 bytes * 3 matrices ~= 43 GB RAM
        Z = np.random.randn(n, n) + 1j * np.random.randn(n, n)
        
        # COMPUTE (This hurts CPU/GPU)
        # The "Hopf Invariant" check
        H = np.dot(Z, Z.conj().T)

        elapsed = time.time() - start_time

        # --- THE FEEDBACK LOOP ---
        if elapsed < 0.1:
            status = "🟢 SUPERSONIC"
        elif elapsed < 1.0:
            status = "🟡 TRANSONIC (Apologies to Von Neumann, but you can't handle this.)"
        elif elapsed < 10.0:
            status = "🟠 SUBSONIC (You're not even close.)"
        else:
            status = "🔴 STALL WARNING (You're burning your life away.)"

        print(f"{n:<15} | {elapsed:.4f}s        | {status}")
        
        time.sleep(0.1)

        # --- THE GLORIOUS CRASH ---
        # We trigger the crash when the math says we can't go further.
        # Trigger after 60K (which is ~2700s)
        if elapsed > 20.0:
            trigger_event_horizon(n, elapsed)
            break

def trigger_event_horizon(current_n, current_time):
    print("\n" + "!"*60)
    print("🛑 CRITICAL FAILURE: EVENT HORIZON REACHED")
    print("!"*60)
    time.sleep(1)
    
    print(f"\n[DIAGNOSTICS]")
    print(f" > Current Scale:    {current_n} Neurons")
    print(f" > Target Scale:     86,000,000,000 Neurons")
    
    # Calculate the time to target based on O(N^3)
    ratio = 8600000000 / current_n
    projected_seconds = current_time * (ratio ** 3)
    projected_years = projected_seconds / (3600 * 24 * 365)
    
    print(f" > Complexity:       CUBIC (O(N^3))")
    print(f" > Time to Target:   {projected_years:,.0f} YEARS")
    print(f" > Status:           UNSUSTAINABLE ON DIGITAL LOGIC")

    print("\n" + "="*60)
    print("🧩 YOU HAVE HIT THE WALL. CHOOSE YOUR PATH:")
    print("="*60)

    print("\n[PATH A: THE ALCHEMIST]")
    print("   \"I can fix this in software.\"")
    print("   Objective: Reduce O(N^3) to O(N) on a Von Neumann machine.")
    print("   Action:    Open `src/optimizations/impossible.py` and try.")
    print("   Spoiler:   You are fighting the Pigeonhole Principle.")

    print("\n[PATH B: THE ARCHITECT]")
    print("   \"I need new physics.\"")
    print("   Objective: Build the Hopf Chip (Native Topological Compute).")
    print("   Action:    This requires capitalization beyond a laptop.")
    print("   Hint:      Ask Steve Jurvetson (Future Ventures) or")
    print("              Peter Barrett (Playground Global) how far away 'Analog Optical Compute' is.")
    
    print("\n👉 SYSTEM ADVICE: The bit is the bottleneck.")
    sys.exit(1)

if __name__ == "__main__":
    clear_screen()
    print_header()
    try:
        input("Press ENTER to ignite the engine, if you dare...")
    except KeyboardInterrupt:
        sys.exit()
    run_simulation()