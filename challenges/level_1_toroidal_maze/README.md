# Level 1: The Toroidal Maze ($T^2$)
### The "Pac-Man" Test

> "If you walk off the edge of the map and fall into the void, you are thinking in Euclidean space. In a true brain, there are no edges, only loops."

#### 1. The Trap: The Edge Problem
Standard Reinforcement Learning (RL) agents are trained on "Flatland" (Euclidean grids). When they hit a wall, they stop. If the world wraps around (like *Pac-Man* or the Earth), a standard agent perceives the "warp" as a teleportation event—a discontinuity that breaks its internal map.

**The Problem:** You cannot build a continuous mind on a discontinuous map.
**The Goal:** Build an agent that natively understands **Toroidal Topology ($T^2$)**.

#### 2. The Physics: Grid Cells
Your brain's GPS (the Entorhinal Cortex) does not use $(x, y)$ coordinates. It uses **Grid Cells**—hexagonal firing patterns that wrap around a torus. This allows you to update your position indefinitely without "running out of graph paper."

#### 3. The Challenge Task
You must train an RL agent to navigate a **20x20 Toroidal Grid** with random obstacles.

* **The World:** A grid where moving **Right** at $x=19$ lands you at $x=0$. Moving **Up** at $y=19$ lands you at $y=0$.
* **The Input:** The agent receives a local view (3x3 grid) and its current "Sense of Direction" (Head Direction). **Crucially, it is NOT given global $(x, y)$ coordinates.**
* **The Objective:** Reach the goal state in the minimum number of steps.

#### 4. The Constraints (The "Physics" Rules)
1.  **No GPS:** You cannot feed the absolute $(x, y)$ coordinate into the neural net.
2.  **No Memory Reset:** The hidden state (LSTM/RNN) must persist across 100 episodes. The agent must realize it is in the *same* continuous space.
3.  **Topological Embeddings:** You are encouraged (but not forced) to encode position using **Rotary Embeddings** or **Phasic Vectors** (e.g., $\sin(x), \cos(x)$) rather than linear scalars.

#### 5. Scoring Criteria

| Level | Method | Outcome | Score |
| :--- | :--- | :--- | :--- |
| **Bronze** | **Standard RL** | The agent learns to navigate but treats the "warp" as a magic portal. It is confused by long distances. | **PASS** |
| **Silver** | **Periodic Padding** | The agent uses Convolutional Neural Networks (CNNs) with circular padding to "see" across the edge. | **GOOD** |
| **Gold** | **Toroidal Manifold** | The agent's internal representation constructs a perfect Torus. If we visualize the latent space , it forms a donut. It navigates the wrap-around as naturally as a straight line. | **MASTER** |

#### 6. Getting Started
```bash
# Clone the repo and install the environment
git clone [https://github.com/HBE-BENCH/hbe-bench.git](https://github.com/HBE-BENCH/hbe-bench.git)
cd hbe-bench
pip install -r requirements.txt

# Run the random agent baseline
python challenges/level_1_toroidal_maze/run_baseline.py