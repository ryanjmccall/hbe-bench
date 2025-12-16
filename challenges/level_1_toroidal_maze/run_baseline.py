import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt

class ToroidalMazeEnv(gym.Env):
    """
    Level 1: The Toroidal Maze
    A grid world where the edges wrap around (Torus topology).
    """
    def __init__(self, grid_size=20):
        super(ToroidalMazeEnv, self).__init__()
        
        self.grid_size = grid_size
        self.agent_pos = np.array([0, 0])
        self.goal_pos = np.array([0, 0])
        
        # Action Space: Up, Down, Left, Right
        self.action_space = spaces.Discrete(4)
        
        # Observation Space: The agent sees its (x, y) coordinates
        # NOTE: In the 'Gold' challenge, users must ignore these raw coords
        # and learn the topology blindly, but for the baseline, we provide them.
        self.observation_space = spaces.Box(
            low=0, high=grid_size-1, shape=(2,), dtype=np.int32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Spawn agent and goal at random distinct locations
        self.agent_pos = np.random.randint(0, self.grid_size, size=2)
        self.goal_pos = np.random.randint(0, self.grid_size, size=2)
        while np.array_equal(self.agent_pos, self.goal_pos):
            self.goal_pos = np.random.randint(0, self.grid_size, size=2)
            
        return self.agent_pos, {}

    def step(self, action):
        # 0: Up, 1: Down, 2: Left, 3: Right
        direction = np.array([0, 0])
        if action == 0: direction = np.array([0, -1])
        if action == 1: direction = np.array([0, 1])
        if action == 2: direction = np.array([-1, 0])
        if action == 3: direction = np.array([1, 0])
        
        # Apply movement
        new_pos = self.agent_pos + direction
        
        # --- THE TOROIDAL MAGIC ---
        # The modulo operator (%) creates the wrap-around effect.
        # If x = 20, 20 % 20 = 0. If x = -1, -1 % 20 = 19.
        self.agent_pos = new_pos % self.grid_size
        # --------------------------
        
        # Check reward
        done = np.array_equal(self.agent_pos, self.goal_pos)
        reward = 10.0 if done else -0.1 # Small penalty to encourage speed
        
        return self.agent_pos, reward, done, False, {}

    def render(self):
        grid = np.zeros((self.grid_size, self.grid_size))
        grid[self.goal_pos[1], self.goal_pos[0]] = 0.5 # Goal
        grid[self.agent_pos[1], self.agent_pos[0]] = 1.0 # Agent
        
        plt.imshow(grid, cmap='hot')
        plt.title(f"Agent: {self.agent_pos} | Goal: {self.goal_pos}")
        plt.axis('off')
        plt.pause(0.1)
        plt.clf()

# --- RUN BASELINE AGENT ---

if __name__ == "__main__":
    env = ToroidalMazeEnv(grid_size=10)
    obs, _ = env.reset()
    
    print(f"--- STARTING TOROIDAL RUN ---")
    print(f"Goal Location: {env.goal_pos}")
    
    steps = 0
    done = False
    
    while not done and steps < 50:
        # Random Agent (The "Drunk" Baseline)
        action = env.action_space.sample()
        obs, reward, done, _, _ = env.step(action)
        
        # Visualizing the "Warp"
        # If the agent jumps from 0 to 9, or 9 to 0, it used the torus.
        print(f"Step {steps}: Action {action} -> Pos {obs}")
        steps += 1
        
        # Uncomment to watch the agent run
        # env.render()
        
    if done:
        print("SUCCESS: Goal Reached!")
    else:
        print("FAIL: Timeout (Entropy Win)")