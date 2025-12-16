# Level 5: The Foundry (Hardware)
### The "Thermal Throttling" Test

> "A mind that works in Python but burns 10,000 Watts is not a solution; it is a fire hazard. The Road to Substrate Independence must pass through the Foundry."

#### 1. The Trap: The Cloud Delusion
Most AI research assumes infinite compute and cooling.
* **The Reality:** The **Hopf Chip** must sit inside a skull or a small biocompatible casing. It has a strict power budget of **1 Watt** and a thermal ceiling of **40°C**.
* **The Failure:** If your model is "Heavy" (Dense Matrix Multiplications), the chip heats up. When it hits 40°C, it **throttles** (slows down).
* **The Consequence:** Throttling breaks Phase Lock (Level 3). The user dies of heatstroke or lag.

#### 2. The Task: Hardware-Aware Integration
You must run the **Level 3 (Handshake)** and **Level 4 (Symphony)** protocols simultaneously, but this time, every mathematical operation costs **Joules** and generates **Heat**.

* **Input:** The same biological signals as before.
* **Constraint:** You operate on the **Virtual Hopf Chip**.
    * **Idle Power:** 0.1 W
    * **Cost per FLOP:** $10^{-12}$ Joules (Simulated Neuromorphic Efficiency)
    * **Cooling Rate:** Passive dissipation (slow).

#### 3. The Metric: Fabrication Yield ($P_{Fab}$)
We measure the probability that your architecture can physically exist.

$$P_{Fab} = \mathbb{I}(\text{Temp} < 40^\circ C) \times \mathbb{I}(\text{Power} < 1W)$$

* **Pass:** The chip runs cool and fast.
* **Fail:** The chip overheats, throttles, and drops the connection ($LTV$ crashes).

#### 4. The Challenge Tiers

| Level | Method | Power / Temp | Description |
| :--- | :--- | :--- | :--- |
| **Bronze** | **Dense Transformer** | 50 W / 100°C | **The GPU.** It tries to run a massive matrix on a tiny chip. **Outcome: Meltdown.** |
| **Silver** | **Quantized RNN** | 2 W / 45°C | **The Mobile Chip.** Better, but still too hot for continuous BCI. It throttles intermittently. **Outcome: Lag/Seizures.** |
| **Gold** | **Sparse / Spiking** | < 0.5 W / 37°C | **The Neuromorphic.** It only fires when information moves (Event-Based). It stays cool. **Outcome: Safe.** |

#### 5. Run the Challenge
```bash
cd challenges/level_5_foundry
python run_foundry.py
```
