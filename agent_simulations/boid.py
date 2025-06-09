import numpy as np
from agent_base import Agent, normalize_vector, limit_vector

class Boid(Agent):
    def __init__(self, x, y, max_speed, max_force, 
                 perception_radius=50.0, 
                 sep_factor=1.5, ali_factor=1.0, coh_factor=1.0):
        super().__init__(x, y, max_speed, max_force, color='cyan', size=8)
        self.perception_radius = perception_radius
        self.separation_factor = sep_factor
        self.alignment_factor = ali_factor
        self.cohesion_factor = coh_factor

    def _get_neighbors(self, boids):
        neighbors = []
        for other in boids:
            if other is self:
                continue
            dist = np.linalg.norm(self.position - other.position)
            if 0 < dist < self.perception_radius:
                neighbors.append(other)
        return neighbors

    def separate(self, neighbors):
        steering = np.zeros(2)
        count = 0
        for other in neighbors:
            dist = np.linalg.norm(self.position - other.position)
            if dist > 0: # Avoid division by zero
                diff = normalize_vector(self.position - other.position)
                diff /= dist  # Weight by distance (closer boids have stronger repulsion)
                steering += diff
                count += 1
        if count > 0:
            steering /= count
            steering = normalize_vector(steering) * self.max_speed
            steering -= self.velocity
            steering = limit_vector(steering, self.max_force)
        return steering

    def align(self, neighbors):
        steering = np.zeros(2)
        count = 0
        for other in neighbors:
            steering += other.velocity
            count += 1
        if count > 0:
            steering /= count
            steering = normalize_vector(steering) * self.max_speed
            steering -= self.velocity
            steering = limit_vector(steering, self.max_force)
        return steering

    def cohesion(self, neighbors):
        center_of_mass = np.zeros(2)
        count = 0
        for other in neighbors:
            center_of_mass += other.position
            count += 1
        if count > 0:
            center_of_mass /= count
            return self.seek(center_of_mass)
        return np.zeros(2)

    def flock(self, boids):
        neighbors = self._get_neighbors(boids)
        
        sep = self.separate(neighbors) * self.separation_factor
        ali = self.align(neighbors) * self.alignment_factor
        coh = self.cohesion(neighbors) * self.cohesion_factor
        
        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)
