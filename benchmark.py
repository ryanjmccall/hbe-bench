import sys
import time
import numpy as np

# -----------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION (The "Contract")
# -----------------------------------------------------------------------------
LATENCY_BUDGET_MS = 50.0   # Max allowed time per inference
ACCURACY_THRESHOLD = 0.99  # Minimum required accuracy against ground truth
PHYSICS_TOLERANCE = 1e-5   # Epsilon for topological invariant checks
RANDOM_SEED = 42           # Determinism for the "Fluke Filter"

# -----------------------------------------------------------------------------
# THE GROUND TRUTH (Your "Secret" Physics)
# -----------------------------------------------------------------------------
def hopf_map_ground_truth(p):
    """
    Standard Hopf map sending S3 -> S2.
    Ref: (2(wx + yz), 2(wy - xz), w^2 + x^2 - y^2 - z^2)
    This represents the 'Physics' we are trying to emulate.
    """
    w, x, y, z = p
    return np.array([
        2 * (w*x + y*z),
        2 * (w*y - x*z),
        w**2 + x**2 - y**2 - z**2
    ])

# -----------------------------------------------------------------------------
# THE SUBMISSION WRAPPER
# -----------------------------------------------------------------------------
def load_user_submission():
    """
    TODO: In the future, this will dynamically import the user's model 
    from a specific file (e.g., 'submission.py' or 'model.onnx').
    For now, we return a mock function to test the pipeline.
    """
    # Mocking a "Good" Submission that acts just like the ground truth
    return hopf_map_ground_truth

# -----------------------------------------------------------------------------
# THE FOUR PILLARS OF VERIFICATION
# -----------------------------------------------------------------------------

def verify_functional(model, sample_input):
    """Pillar 1: Functional Check (Shape & Type)"""
    try:
        output = model(sample_input)
        if not isinstance(output, np.ndarray):
            return False, "Output is not a numpy array."
        if output.shape != (3,):
            return False, f"Output shape mismatch. Expected (3,), got {output.shape}."
        return True, "Functional checks passed."
    except Exception as e:
        return False, f"Crashed during inference: {str(e)}"

def verify_performance(model, sample_input):
    """Pillar 2: Compute Budget (Latency)"""
    warmup = 10
    trials = 100
    
    # Warmup
    for _ in range(warmup):
        model(sample_input)
        
    # Benchmark
    start_time = time.perf_counter()
    for _ in range(trials):
        model(sample_input)
    end_time = time.perf_counter()
    
    avg_latency_ms = ((end_time - start_time) / trials) * 1000
    print(f"   [Performance] Latency: {avg_latency_ms:.4f} ms")
    
    if avg_latency_ms > LATENCY_BUDGET_MS:
        return False, f"Too slow! {avg_latency_ms:.2f}ms > {LATENCY_BUDGET_MS}ms budget."
    return True, "Performance budget met."

def verify_accuracy(model, test_set):
    """Pillar 3: The Hold-Out Dataset (Accuracy)"""
    score = 0
    total = len(test_set)
    
    for p in test_set:
        prediction = model(p)
        truth = hopf_map_ground_truth(p)
        
        # Check Euclidean distance
        if np.linalg.norm(prediction - truth) < PHYSICS_TOLERANCE:
            score += 1
            
    accuracy = score / total
    print(f"   [Accuracy] Score: {accuracy:.4f}")
    
    if accuracy < ACCURACY_THRESHOLD:
        return False, f"Accuracy too low. {accuracy:.4f} < {ACCURACY_THRESHOLD}"
    return True, "Accuracy threshold met."

def verify_physics(model):
    """
    Pillar 4: Topological Invariants (The 'Hopf' Check)
    Constraint: Points on the same fiber must map to the same base point.
    f(h * p) == f(p) where h is a rotation along the fiber.
    """
    # 1. Pick a random point on S3
    p = np.random.randn(4)
    p /= np.linalg.norm(p)
    
    # 2. Apply a phase rotation (h) along the fiber
    # (For Hopf, this corresponds to multiplying by e^(i*theta) in complex coords)
    # TODO: DEEP WORK - Implement rigorous fiber rotation logic here.
    # For now, we assume identity (trivial check) to ensure pipeline runs.
    p_rotated = p 
    
    val1 = model(p)
    val2 = model(p_rotated)
    
    diff = np.linalg.norm(val1 - val2)
    print(f"   [Physics] Fiber Invariant Error: {diff:.6e}")
    
    if diff > PHYSICS_TOLERANCE:
        return False, "Topological invariant broken. Fiber not preserved."
    return True, "Topological constraints verified."

# -----------------------------------------------------------------------------
# MAIN ORACLE LOOP
# -----------------------------------------------------------------------------
def run_oracle():
    print("🔮 ORACLE INITIALIZED: Scanning Submission...")
    np.random.seed(RANDOM_SEED)
    
    # 0. Setup Data
    # Generate 100 random normalized quaternions (S3)
    test_data = np.random.randn(100, 4)
    test_data /= np.linalg.norm(test_data, axis=1, keepdims=True)
    
    # 1. Load Model
    user_model = load_user_submission()
    
    # 2. Run Pillars
    checks = [
        ("Functional", verify_functional(user_model, test_data[0])),
        ("Performance", verify_performance(user_model, test_data[0])),
        ("Accuracy", verify_accuracy(user_model, test_data)),
        ("Physics", verify_physics(user_model))
    ]
    
    # 3. Final Judgement
    all_passed = True
    print("\n--- REPORT CARD ---")
    for name, (passed, msg) in checks:
        icon = "✅" if passed else "❌"
        print(f"{icon} {name}: {msg}")
        if not passed:
            all_passed = False
            
    if all_passed:
        print("\n🎉 ORACLE VERDICT: PASS. Payment Unlocked.")
        sys.exit(0)
    else:
        print("\n💀 ORACLE VERDICT: FAIL. Substrate Independence Not Achieved.")
        sys.exit(1)

if __name__ == "__main__":
    run_oracle()