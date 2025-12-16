import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

def generate_synthetic_brain_data(n_timepoints=2000, n_neurons=500):
    """
    Generates synthetic calcium traces that mimic ZAPBench statistics.
    Used for rapid local testing without downloading 5TB of data.
    """
    np.random.seed(42)
    t = np.linspace(0, 100, n_timepoints)
    
    # Simulate neurons as sine waves (oscillators) + biological noise
    # This mimics the 'Stuart-Landau' dynamics often used in Hopf models
    signals = np.sin(t[:, None] + np.random.rand(1, n_neurons) * 2 * np.pi) 
    noise = np.random.normal(0, 0.2, (n_timepoints, n_neurons))
    
    return signals + noise

def run_linear_benchmark():
    print("⚔️  Initializing Baseline Protocol (Ridge Regression)...")
    
    # 1. Setup Data
    print("   [Data] Generating Synthetic Neural Traces...")
    signals = generate_synthetic_brain_data()
    
    # 2. Create Features (Lagged History)
    # We use the past 5 timepoints to predict the next 1
    lag = 5
    X, y = [], []
    for i in range(lag, len(signals)):
        X.append(signals[i-lag:i].flatten()) # Input: History [t-5 ... t-1]
        y.append(signals[i])                 # Target: Current [t]
        
    X = np.array(X)
    y = np.array(y)
    
    # 3. Split
    # We do a chronological split (Training on past, Testing on future)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # 4. Train (The "Standard" Euclidean Model)
    print("   [Training] Fitting Linear Model...")
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    print("   [Evaluating] Forecasting Future Activity...")
    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)
    
    print(f"\n📊 BASELINE RESULTS")
    print(f"   ----------------")
    print(f"   Model: Euclidean Ridge Regression")
    print(f"   R² Score: {score:.4f}")
    
    if score > 0.40:
        print("   Status: 🔴 STRONG BASELINE. (The Hopf Model has a real fight ahead)")
    else:
        print("   Status: 🟢 WEAK BASELINE. (Prime candidate for Topological improvement)")

if __name__ == "__main__":
    run_linear_benchmark()
