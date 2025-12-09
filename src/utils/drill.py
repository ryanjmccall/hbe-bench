import time
import random
import os

# The Knowledge Base
flashcards = {
    "Space-Time Hopfion": "A 3D topological soliton (knot) that persists through time.",
    "Hopf Fibration": "A map from S3 to S2; filling space with linked circles.",
    "Skyrmion": "A 2D vortex-like topological particle protected by winding number.",
    "OAM (Orbital Angular Momentum)": "Light with a twisted wavefront (helical phase).",
    "Manifold": "A shape that looks Euclidean locally but curved globally.",
    "Topological Protection": "Robustness against noise due to global structure (cannot untie the knot)."
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def start_dojo():
    clear()
    print("🥋 WELCOME TO THE DOJO")
    print("   Internalizing the Kernel Symbols...")
    print("---------------------------------------")
    time.sleep(1)

    items = list(flashcards.items())
    random.shuffle(items)
    
    score = 0
    for term, definition in items:
        print(f"\n[TERM]:  {term}")
        input(">> Press Enter to reveal...")
        
        print(f"[TRUTH]: {definition}")
        
        rating = input("\nDid you know this? (y/n): ").lower()
        if rating == 'y':
            score += 1
            print("✅ Good.")
        else:
            print("❌ Study harder.")
        
        print("-" * 40)
        time.sleep(0.5)

    print(f"\nTraining Complete. Score: {score}/{len(items)}")
    if score == len(items):
        print("🏆 You are ready for Phase 2.")

if __name__ == "__main__":
    start_dojo()