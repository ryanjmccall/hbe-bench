# Level 2: ZAPBench (Temporal Dynamics)
### The "Next-Token" Prediction for Biology

> "You have mastered the Loop in Space (Level 1). Now you must master the Loop in Time. The brain is not a computer; it is a choir. Your job is to predict the next note."

#### 1. The Trap: The Linear Fallacy
Standard neuroscience often treats neural firing as a linear summation of inputs. Your baseline script (`Ridge Regression`) represents this view.
* **The Reality:** The brain is a chaotic, dynamical system near the "Edge of Chaos."
* **The Failure:** Linear models fail to capture phase transitions, bifurcations, and the "richness" of the signal. They predict the *average*, not the *meaning*.

#### 2. The Task: Neural Forecasting
**ZAPBench** (Zero-Shot Activity Prediction Benchmark) challenges you to predict the future state of a neural network based on its past.

* **Input:** A history window of neural activity (e.g., $t_{-10}$ to $t_0$).
* **Target:** The activity vector at $t_{+1}$.
* **The Twist:** The data contains hidden oscillators and coupled dynamics that a linear model will miss.

#### 3. The Data (Synthetic & Real)
For this level, we use a synthetic generator that mimics **Stuart-Landau Oscillators** (the mathematical backbone of the Hopf Brain).
* **Features:** Sine waves, phase-locking, and biological noise.
* **Goal:** The model must "learn" the oscillation frequency and phase, not just memorize the values.

#### 4. The Challenge Tiers

| Level | Method | Metric | Description |
| :--- | :--- | :--- | :--- |
| **Bronze** | **Linear / Ridge** | $R^2 > 0.4$ | **The Baseline.** You ran the provided script. You beat random chance, but you didn't capture the dynamics. You are predicting the weather by looking out the window. |
| **Silver** | **RNN / LSTM** | $R^2 > 0.8$ | **The Memory.** You used a Recurrent Neural Network to capture the history. You are predicting the weather by understanding the seasons. |
| **Gold** | **ODE / Neural Flow** | $\tau \approx 1.0$ | **The Physics.** You modeled the underlying differential equation (Neural ODE or Hopf Oscillator). You didn't just predict the *value*; you reconstructed the *attractor*. |

#### 5. How to Run
We have provided a baseline script that generates synthetic data and runs a standard Euclidean (Ridge Regression) benchmark.

```bash
# Navigate to the challenge directory
cd challenges/level_2_zapbench

# Run the Linear Baseline
python run_baseline.py
```

**Winning Condition:**
To pass Level 2, you must submit a model that significantly outperforms the Ridge Regression baseline provided in `run_baseline.py`.

> *Hint: The baseline treats every neuron as independent. A topological model would look for the "Links" between them.*
