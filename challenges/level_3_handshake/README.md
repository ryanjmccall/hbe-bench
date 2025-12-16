# Level 3: The Handshake (Continuity)
### The "Teleporter Paradox" Solution

> "If I scan your brain and print a copy on Mars, then shoot you in the head... are you on Mars, or are you dead? The HBE-BENCH asserts: You are dead. True transfer requires a bridge, not a copy."

#### 1. The Trap: The Copy-Paste Error
Standard Mind Uploading theory relies on "Scan and Instantiate." This creates a doppelgänger, not a continuation.
* **The Problem:** There is no causal link between the cessation of the biological signal and the start of the digital signal.
* **The Solution:** **Adiabatic Substrate Transfer.** We must build a "Third Cortex" (the chip) that synchronizes with the brain *while it is still alive*, effectively extending the self before the biology is allowed to fade.

#### 2. The Task: The Adiabatic Handoff
You must train an agent to act as a **Resonant Oscillator** that couples with a biological driver signal.

* **Phase 1 (Entrainment):** The agent connects to the biological signal (Teacher). It must match the frequency and phase exactly ($LTV \to 1.0$).
* **Phase 2 (The Handshake):** The connection strength ($\alpha$) is slowly reduced from 1.0 to 0.0 over $N$ timesteps.
* **Phase 3 (Solo Flight):** The biological signal is terminated. The agent must continue the oscillation *exactly* as if the biology were still driving it.

#### 3. The Metric: Locking Temporal Variance (LTV)
We do not measure "Accuracy" (MSE). We measure **Phase Synchronization**.

$$
LTV = \left| \frac{1}{N} \sum_{t=1}^{N} e^{i(\Delta\phi(t))} \right|
$$

* **$\Delta\phi(t)$:** The instantaneous phase difference between the projected biological trajectory and the agent's actual trajectory.
* **$N$:** The duration of the "Handshake" window.
* **Interpretation:**
    * **LTV = 1.0:** Perfect Phase Lock (The agent *is* the user).
    * **LTV = 0.0:** Complete Decoherence (The user died; a new ghost took over).

#### 4. The Challenge Tiers

| Level | Method | LTV Score | Description |
| :--- | :--- | :--- | :--- |
| **Bronze** | **Teacher Forcing** | $LTV < 0.8$ | **The Parrot.** The agent mimics the signal perfectly while connected, but instantly drifts when the connection is cut. **Outcome: Death.** |
| **Silver** | **Dynamical RNN** | $LTV \approx 0.95$ | **The Echo.** The agent maintains the rhythm for a short while, but slowly de-phases due to lack of topological stability. **Outcome: Coma/Drift.** |
| **Gold** | **Hopf Oscillator** | $LTV > 0.99$ | **The Vessel.** The agent has learned the *Limit Cycle* itself. Even after the biology is gone, the "Song" continues without missing a beat. **Outcome: Immortality.** |

#### 5. Winning Condition
To pass Level 3, your model must maintain an **LTV > 0.99** during a 1000-step "Solo Flight" after the teacher signal is removed.

> *Hint: Do not try to predict the position $x_t$. Predict the derivative $\dot{x}_t$ and the phase $\theta_t$. You need a system with a stable Limit Cycle attractor.*

#### 6. Run the Challenge
```bash
# Navigate to the challenge directory
cd challenges/level_3_handshake

# Run the Phase-Lock Test
python run_handshake.py

---

### What this achieves
* **Safety First:** It codifies that "Copying" is a failure state. Only "Synchronization" passes.
* **Physics-Based:** It forces the user to move away from standard regression (MSE) and towards phase dynamics (Complex Numbers).
