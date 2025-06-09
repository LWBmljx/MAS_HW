import numpy as np
from agent_base import Agent

class Evader(Agent):
    def __init__(self, x, y, max_speed, max_force, flee_radius=150.0):
        super().__init__(x, y, max_speed, max_force, color='red', size=9)
        self.flee_radius = flee_radius

    def update_behavior(self, pursuers):
        flee_force_total = np.zeros(2)
        closest_pursuer_dist = float('inf')
        closest_pursuer_pos = None

        for p_list in pursuers: 
            for p in p_list if isinstance(p_list, list) else [p_list]: 
                dist = np.linalg.norm(self.position - p.position)
                if dist < closest_pursuer_dist:
                    closest_pursuer_dist = dist
                    closest_pursuer_pos = p.position
        
        if closest_pursuer_pos is not None and closest_pursuer_dist < self.flee_radius:
            flee_force_total = self.flee(closest_pursuer_pos, self.flee_radius)

        if np.linalg.norm(flee_force_total) < 0.01: 
            random_force = (np.random.rand(2) - 0.5) * self.max_force * 0.1 
            self.apply_force(random_force)

        self.apply_force(flee_force_total)

class Pursuer(Agent):
    def __init__(self, x, y, max_speed, max_force):
        super().__init__(x, y, max_speed, max_force, color='blue', size=9)

    def update_behavior(self, evader):
        pursuit_force = self.seek(evader.position)
        self.apply_force(pursuit_force)
