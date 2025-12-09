import time
import random
import os

# The Knowledge Base
topics = {
    "Topology Basics": [
        {
            "term": "Genus (g)",
            "definition": "Number of holes in a topological space.",
            "level2_q": "Calculate the genus of a surface with Euler Characteristic chi = -2. (Hint: chi = 2 - 2g)",
            "level2_a": "2",
            "level3_q": "How does increasing the genus of a material affect its potential for connectivity in a network?",
            "level3_a": "Higher genus allows for more non-intersecting paths and complex routing without crossing."
        },
        {
            "term": "Euler Characteristic (chi)",
            "definition": "Topological invariant; chi = V - E + F (polyhedra) or 2 - 2g (surfaces).",
            "level2_q": "A cube has V=8, E=12, F=6. Calculate its Euler Characteristic.",
            "level2_a": "2",
            "level3_q": "Why is the Euler Characteristic considered a 'checksum' for shape integrity?",
            "level3_a": "It remains constant regardless of how you mesh the surface, detecting errors in geometry."
        },
        {
            "term": "Topological Invariant",
            "definition": "Property unchanged under continuous deformation (stretching/bending) but not tearing/gluing.",
            "level2_q": "Is 'Volume' a topological invariant? (yes/no)",
            "level2_a": "no",
            "level3_q": "Why do we care about invariants in computing?",
            "level3_a": "They provide robust states for memory that are immune to local noise/deformations."
        },
        {
            "term": "Sphere (P=0)",
            "definition": "Can be shrunk to a point, zero holes.",
            "level2_q": "Code fix: `def is_contractible(genus): return genus > 0` (Enter the correct return statement)",
            "level2_a": "return genus == 0",
            "level3_q": "Why is the sphere the 'trivial' vacuum state of topology?",
            "level3_a": "It contains no topological features/holes to store information or trap fields."
        },
        {
            "term": "Torus (P=1)",
            "definition": "Donut, 1 hole possible, path trace around the hole that can't be shrunk to a point.",
            "level2_q": "Can a loop drawn around the hole of a donut be shrunk to a point? (yes/no)",
            "level2_a": "no",
            "level3_q": "How does the non-trivial loop of a torus enable persistent memory storage?",
            "level3_a": "The loop represents a stable state that cannot decay into the trivial state without a phase transition."
        },
        {
            "term": "Topologically Distinct (P=0 vs P=1)",
            "definition": "P=0 and P=1 are topologically distinct spaces.",
            "level2_q": "Can you transform a mug (g=1) into a donut (g=1) continuously? (yes/no)",
            "level2_a": "yes",
            "level3_q": "What prevents a P=0 state from spontaneously turning into a P=1 state?",
            "level3_a": "An energy barrier associated with tearing the manifold to create a hole."
        },
        {
            "term": "Double Torus (P=2)",
            "definition": "A shape with two holes.",
            "level2_q": "If you glue two tori together side-by-side, what is the resulting genus?",
            "level2_a": "2",
            "level3_q": "What advantage does a Double Torus offer over a single Torus for quantum computing?",
            "level3_a": "It offers a larger state space (degeneracy) for encoding qubits, potentially allowing for error correction."
        },
        {
            "term": "Manifold",
            "definition": "A shape that looks Euclidean locally but curved globally.",
            "level2_q": "Is the surface of the earth a manifold? (yes/no)",
            "level2_a": "yes",
            "level3_q": "Why is the concept of a manifold essential for General Relativity?",
            "level3_a": "It allows us to describe gravity as the curvature of spacetime (a 4-manifold) rather than a force."
        }
    ],
    "Physics & Solitons": [
        {
            "term": "Space-Time Hopfion",
            "definition": "A 3D topological soliton (knot) that persists through time.",
            "level2_q": "Is a Hopfion a static structure or a dynamic process?",
            "level2_a": "dynamic",
            "level3_q": "How does a Hopfion differ from a standard particle wave-packet?",
            "level3_a": "A Hopfion's stability comes from its knot topology, whereas a wave-packet disperses over time."
        },
        {
            "term": "Skyrmion",
            "definition": "Stable, swirling field configuration behaving like a particle, protected by topology from disappearing.",
            "level2_q": "If a Skyrmion has a winding number of 0, is it topologically stable? (yes/no)",
            "level2_a": "no",
            "level3_q": "Why can a Skyrmion survive thermal noise that would scramble a standard magnetic bit?",
            "level3_a": "To destroy it, you must unwind the entire field configuration, which requires overcoming a global energy barrier."
        },
        {
            "term": "Hopf Charge (Skyrmion Knot)",
            "definition": "For 3D skyrmions (hopfions), the 'knot' is described by the Hopf charge or linking number.",
            "level2_q": "What integer represents a trivial knot (no knot)?",
            "level2_a": "0",
            "level3_q": "What does the conservation of Hopf charge imply for physical systems?",
            "level3_a": "It implies that the number of knots/particles is conserved during continuous evolution, preventing decay."
        },
        {
            "term": "Topological Protection",
            "definition": "Robustness against noise due to global structure (cannot untie the knot).",
            "level2_q": "Does cutting a knot preserve its topological protection? (yes/no)",
            "level2_a": "no",
            "level3_q": "How is topological protection analogous to a knot in a rope?",
            "level3_a": "Small shakes (noise) won't untie the knot; you have to cut the rope (high energy) to remove it."
        },
        {
            "term": "Cowlick Analogy",
            "definition": "Applies to Skyrmion due to swirling nature and directionality of spin texture.",
            "level2_q": "Can you comb a hairy ball flat without any cowlicks? (yes/no)",
            "level2_a": "no",
            "level3_q": "What does the 'Cowlick' represent in the field theory?",
            "level3_a": "It represents a singularity or a topological defect where the field direction is undefined or vanishes."
        }
    ],
    "Advanced Geometry": [
        {
            "term": "Hopf Fibration",
            "definition": "Map decomposing S3 (in 4D) into interlocking circles (fibers); tori emerge within its structure.",
            "level2_q": "In the Hopf Fibration, what shape do the fibers map to in the base space S2?",
            "level2_a": "points",
            "level3_q": "Why is the Hopf Fibration called the 'source code' of 3D knots?",
            "level3_a": "It defines the fundamental way 3D space can be structured with linked loops, generating non-trivial topology."
        },
        {
            "term": "Nested Tori",
            "definition": "Hopf fibration fills 3D space with nested tori.",
            "level2_q": "Do these nested tori ever intersect each other? (yes/no)",
            "level2_a": "no",
            "level3_q": "Visualizing 3D space as filled with nested tori helps us understand what physical property?",
            "level3_a": "The structure of complex flow fields or electromagnetic field lines in a knotted configuration."
        },
        {
            "term": "Fibers as Loops",
            "definition": "Each nested torus is composed of Hopf circles (fibers).",
            "level2_q": "Are these fibers linked with each other? (yes/no)",
            "level2_a": "yes",
            "level3_q": "What is the significance of every pair of fibers being linked exactly once?",
            "level3_a": "It signifies the non-trivial Hopf invariant (linking number = 1), the simplest non-trivial map from S3 to S2."
        },
        {
            "term": "OAM (Orbital Angular Momentum)",
            "definition": "Light with a twisted wavefront (helical phase).",
            "level2_q": "Does OAM depend on polarization (spin)? (yes/no)",
            "level2_a": "no",
            "level3_q": "How does OAM allow for infinite data density?",
            "level3_a": "The twist (topological charge) is an integer that can be arbitrarily large, providing an infinite alphabet."
        }
    ],
    "Optical Topology": [
        {
            "term": "Chirality",
            "definition": "Handedness of the skyrmion spin.",
            "level2_q": "If you mirror a right-handed skyrmion, what do you get? (left-handed/right-handed)",
            "level2_a": "left-handed",
            "level3_q": "Why does chirality matter in spintronics?",
            "level3_a": "It determines the direction of motion under current (Hall effect)."
        },
        {
            "term": "Optical Hopfion",
            "definition": "'Flying' knots in a waveguide.",
            "level2_q": "Are optical hopfions static or propagating?",
            "level2_a": "propagating",
            "level3_q": "How do you generate an optical hopfion?",
            "level3_a": "By interfering structured light beams to create a 3D polarization knot."
        },
        {
            "term": "Space-Time Hopfion Crystal",
            "definition": "Maintained by temporal beat.",
            "level2_q": "What stabilizes this crystal structure?",
            "level2_a": "temporal beat",
            "level3_q": "How does the temporal beat prevent decay?",
            "level3_a": "Resonance with the driving frequency maintains the energy of the topological structure."
        },
        {
            "term": "Soliton",
            "definition": "Self-reinforcing wave packet that maintains its shape while propagating.",
            "level2_q": "Does a soliton disperse like a normal wave? (yes/no)",
            "level2_a": "no",
            "level3_q": "What balances the dispersion in a soliton?",
            "level3_a": "Nonlinearity in the medium balances the dispersion."
        },
        {
            "term": "Frequency Comb",
            "definition": "Frequency distribution where some bands spike in time.",
            "level2_q": "What does the spectrum of a frequency comb look like?",
            "level2_a": "discrete lines",
            "level3_q": "How are frequency combs used in metrology?",
            "level3_a": "They provide a ruler for light, allowing precise measurement of optical frequencies."
        },
        {
            "term": "Space-Time Optical Hopfion (P, Q)",
            "definition": "Data structure from bits to knots; Space (P) and Time (Q).",
            "level2_q": "What do P and Q represent?",
            "level2_a": "topological charges",
            "level3_q": "How does this structure encode information?",
            "level3_a": "Through the linking numbers P (spatial) and Q (temporal) which are conserved integers."
        },
        {
            "term": "Hopfion Construction",
            "definition": "Skyrmion (vortex) -> String (extrusion) -> Closed and Twisted (Hopfion).",
            "level2_q": "What is the intermediate stage between a Skyrmion and a Hopfion?",
            "level2_a": "string",
            "level3_q": "Why must the tube be twisted before gluing?",
            "level3_a": "To create the Hopf invariant (linking number) that protects the knot."
        }
    ]
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear()
    print("🥋 WELCOME TO THE DOJO")
    print("   Internalizing the Kernel Symbols...")
    print("---------------------------------------")
    time.sleep(1)

def select_topic():
    print("\n[THE DECK PHASE]")
    print("Select a learning topic:")
    topic_names = list(topics.keys())
    for i, name in enumerate(topic_names):
        print(f"{i+1}. {name}")
    
    while True:
        try:
            choice = int(input("\n>> Choose (1-3): "))
            if 1 <= choice <= len(topic_names):
                return topic_names[choice-1]
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

def play_level_1(item):
    print(f"\n[LEVEL 1: WARM-UP]")
    print(f"Term: {item['term']}")
    input(">> Press Enter to reveal definition...")
    print(f"[TRUTH]: {item['definition']}")
    
    rating = input("\nDid you know this? (y/n): ").lower()
    if rating == 'y':
        print("Correct.")
        return True
    else:
        print("Incorrect.")
        return False

def play_level_2(item):
    print(f"\n[LEVEL 2: APPLICATION]")
    print(f"Challenge: {item['level2_q']}")
    
    user_ans = input(">> Your Answer: ").strip()
    
    # Simple normalization for checking
    # If answer is code, we might need looser check, but for now exact or contained
    if item['level2_a'].lower() in user_ans.lower():
        print("✅ Correct! Optimization/Fix applied.")
        return True
    else:
        print(f"Incorrect. Expected: {item['level2_a']}")
        return False

def play_level_3(item):
    print(f"\n[LEVEL 3: BOSS MODE]")
    print(f"Synthesis: {item['level3_q']}")
    input(">> Press Enter to reveal insight...")
    print(f"💡 Insight: {item['level3_a']}")
    return True

def celebrate():
    print("\n" + "*"*40)
    print("🎉 GOOD JOB! YOU COMPLETED A ROUND! 🎉")
    print("*"*40)
    time.sleep(1)

def start_dojo():
    print_header()
    
    while True:
        topic_name = select_topic()
        print(f"\nLoading Deck: {topic_name}...")
        time.sleep(1)
        
        deck = topics[topic_name]
        random.shuffle(deck)
        
        score = 0
        max_score = len(deck) * 3 # 3 levels per item roughly, though scoring is simplified
        
        for item in deck:
            print("\n" + "="*40)
            # Level 1
            if play_level_1(item):
                # Level 2
                time.sleep(0.5)
                if play_level_2(item):
                    # Level 3
                    time.sleep(0.5)
                    play_level_3(item)
            
            time.sleep(1)
        
        celebrate()
        
        cont = input("\n⚔️  Up for another round? (y/n): ").lower()
        if cont != 'y':
            print("Exiting Dojo. Rest well, warrior.")
            break
        clear()

if __name__ == "__main__":
    start_dojo()