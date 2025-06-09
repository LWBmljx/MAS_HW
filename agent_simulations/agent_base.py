import numpy as np
import random
import matplotlib.pyplot as plt

from utils import limit_vector, normalize_vector 

class Agent:
    def __init__(self, x, y, max_speed, max_force, color='blue', size=5):
        self.position = np.array([float(x), float(y)])
        self.velocity = (np.random.rand(2) - 0.5) * 2 
        self.velocity = normalize_vector(self.velocity) * random.uniform(0, max_speed)
        if np.linalg.norm(self.velocity) == 0:
            self.velocity = np.array([1.0, 0.0]) * random.uniform(0.1, max_speed)
            
        self.acceleration = np.zeros(2)
        self.max_speed = float(max_speed)
        self.max_force = float(max_force)
        self.color = color
        self.size = size 
        self.history = [] 

    def apply_force(self, force):
        self.acceleration += force

    def update(self):
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0  
        
        self.history.append(self.position.copy())
        if len(self.history) > 50: 
            self.history.pop(0)

    def seek(self, target_pos):
        desired_velocity = normalize_vector(target_pos - self.position) * self.max_speed
        steering_force = desired_velocity - self.velocity
        steering_force = limit_vector(steering_force, self.max_force)
        return steering_force

    def flee(self, target_pos, flee_radius=100.0):
        dist = np.linalg.norm(target_pos - self.position)
        if dist < flee_radius: 
            desired_velocity = normalize_vector(self.position - target_pos) * self.max_speed
            steering_force = desired_velocity - self.velocity
            steering_force = limit_vector(steering_force, self.max_force)
            return steering_force
        return np.zeros(2)

    def edges(self, width, height):
        '''Wraps agent position around the screen edges.'''
        if self.position[0] > width:
            self.position[0] = 0
            self.history.clear() 
        elif self.position[0] < 0:
            self.position[0] = width
            self.history.clear()
        if self.position[1] > height:
            self.position[1] = 0
            self.history.clear()
        elif self.position[1] < 0:
            self.position[1] = height
            self.history.clear()

    def display(self, ax):
        '''Draws the agent as a triangle pointing in the direction of velocity.'''
        if np.linalg.norm(self.velocity) < 0.01:
            shape = plt.Circle(self.position, self.size / 2, color=self.color)
        else:
            angle = np.arctan2(self.velocity[1], self.velocity[0])
            points = np.array([
                [self.size, 0],  
                [-self.size / 2, -self.size / 3], 
                [-self.size / 2, self.size / 3]  
            ])
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle),  np.cos(angle)]
            ])
            transformed_points = points @ rotation_matrix.T + self.position
            shape = plt.Polygon(transformed_points, color=self.color)
        ax.add_patch(shape)
        
        if len(self.history) > 1:
            hist_arr = np.array(self.history)
            ax.plot(hist_arr[:,0], hist_arr[:,1], color=self.color, alpha=0.3, linewidth=0.5)
