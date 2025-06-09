from matplotlib import pyplot as plt
import numpy as np
from agent_base import Agent, limit_vector

class Pedestrian(Agent):
    def __init__(self, x, y, max_speed, max_force, destination,
                 fov_degrees=120, d_max_collision_dist=50, num_fov_samples=20, arrival_threshold=5.0,
                 color='green', size=7):
        super().__init__(x, y, max_speed, max_force, color=color, size=size)
        self.destination = np.array(destination, dtype=float)
        self.fov_radians = np.radians(fov_degrees / 2.0) # This is phi from the description
        self.d_max_collision_dist = float(d_max_collision_dist)
        self.num_fov_samples = int(num_fov_samples)
        self.arrival_threshold = float(arrival_threshold)
        self.is_arrived = False

    def _get_direction_to_destination(self):
        if self.is_arrived:
            return np.zeros(2)
        direction_to_dest = self.destination - self.position
        dist_to_dest = np.linalg.norm(direction_to_dest)

        if dist_to_dest < self.arrival_threshold:
            self.is_arrived = True
            return np.zeros(2)
        if dist_to_dest < 1e-5: # Effectively at destination
            self.is_arrived = True # Also set arrived here
            return np.zeros(2)
        return direction_to_dest / dist_to_dest

    def _distance_to_first_obstacle_in_direction(self, alpha_world_angle, static_obstacles, other_pedestrians):
        """
        Calculates f(alpha) - distance to the first obstacle in the direction alpha (world angle).
        Obstacles include static_obstacles and other_pedestrians.
        """
        min_dist_to_collision = self.d_max_collision_dist
        direction_vector = np.array([np.cos(alpha_world_angle), np.sin(alpha_world_angle)])

        # Check static obstacles
        for obs in static_obstacles: # obs is {'position': np.array, 'radius': float}
            # Ray-sphere intersection
            vec_agent_to_obs_center = obs['position'] - self.position
            # Project vec_agent_to_obs_center onto direction_vector
            t_center = np.dot(vec_agent_to_obs_center, direction_vector)
            
            if t_center < 0 and np.linalg.norm(vec_agent_to_obs_center) > obs['radius'] + self.size : # Obstacle is behind and not overlapping
                continue

            dist_squared_center_to_ray = np.linalg.norm(vec_agent_to_obs_center)**2 - t_center**2
            
            # If ray misses the obstacle's bounding sphere for collision check
            if dist_squared_center_to_ray > (obs['radius'] + self.size/2)**2: # Consider agent's size
                continue
            
            # Distance from t_center to intersection point on ray from obstacle center
            t_half_chord_squared = (obs['radius'] + self.size/2)**2 - dist_squared_center_to_ray
            if t_half_chord_squared < 0: # Should be caught by previous check, but for safety
                continue
                
            t_intersection = t_center - np.sqrt(t_half_chord_squared)
            
            if t_intersection >= 0 and t_intersection < min_dist_to_collision:
                min_dist_to_collision = t_intersection

        # Check other pedestrians (simplified as spheres for collision)
        for other_ped in other_pedestrians:
            if other_ped is self:
                continue
            
            vec_agent_to_other_center = other_ped.position - self.position
            t_center_other = np.dot(vec_agent_to_other_center, direction_vector)

            if t_center_other < 0 and np.linalg.norm(vec_agent_to_other_center) > other_ped.size + self.size: # Other is behind and not overlapping
                continue

            dist_sq_center_to_ray_other = np.linalg.norm(vec_agent_to_other_center)**2 - t_center_other**2
            
            combined_radius_sq = ((self.size + other_ped.size) / 2.0)**2 # Collision when centers are this close
            if dist_sq_center_to_ray_other > combined_radius_sq:
                continue

            t_half_chord_sq_other = combined_radius_sq - dist_sq_center_to_ray_other
            if t_half_chord_sq_other < 0:
                continue
            
            t_intersection_other = t_center_other - np.sqrt(t_half_chord_sq_other)

            if t_intersection_other >= 0 and t_intersection_other < min_dist_to_collision:
                min_dist_to_collision = t_intersection_other
                
        return min_dist_to_collision

    def _calculate_best_direction_vector(self, static_obstacles, other_pedestrians):
        if self.is_arrived:
            return np.zeros(2)

        vec_to_dest_normalized = self._get_direction_to_destination()
        if np.linalg.norm(vec_to_dest_normalized) < 1e-5:
            self.is_arrived = True
            return np.zeros(2)

        # "正前方" (forward direction) is the current velocity direction, or direction to destination if not moving
        if np.linalg.norm(self.velocity) > 0.01:
            current_forward_angle = np.arctan2(self.velocity[1], self.velocity[0])
        else:
            current_forward_angle = np.arctan2(vec_to_dest_normalized[1], vec_to_dest_normalized[0])

        best_cost = float('inf')
        chosen_direction_vector = vec_to_dest_normalized # Default to direct path to destination

        if self.num_fov_samples <= 0:
             return vec_to_dest_normalized

        # Alpha (α) represents possible directions within the FOV [-phi, phi] relative to forward direction
        for i in range(self.num_fov_samples):
            # angle_alpha_relative is the 'α' from the description, relative to agent's forward direction
            angle_alpha_relative = np.linspace(-self.fov_radians, self.fov_radians, self.num_fov_samples)[i]
            # Convert alpha to a world angle
            candidate_world_angle = current_forward_angle + angle_alpha_relative
            candidate_world_angle = (candidate_world_angle + np.pi) % (2 * np.pi) - np.pi # Normalize

            # f(alpha) - distance to first obstacle in this candidate_world_angle
            f_alpha = self._distance_to_first_obstacle_in_direction(candidate_world_angle, static_obstacles, other_pedestrians)

            # Cost function: The description implies choosing alpha that minimizes some function of f(alpha)
            # and alignment with destination. Let's use the cost from hw6.ipynb's pedestrian example,
            # which tries to balance avoiding obstacles and reaching the destination.
            # Angle difference between candidate_world_angle and the angle towards the ultimate destination O_i
            angle_to_destination_Oi = np.arctan2(vec_to_dest_normalized[1], vec_to_dest_normalized[0])
            angle_diff_candidate_to_Oi = candidate_world_angle - angle_to_destination_Oi
            angle_diff_candidate_to_Oi = (angle_diff_candidate_to_Oi + np.pi) % (2 * np.pi) - np.pi
            
            # Cost function from the image/description is not fully specified, using a common one:
            # d = d_max^2 + f(alpha)^2 - 2 * d_max * f(alpha) * cos(angle_diff_candidate_to_Oi)
            # This cost function is minimized when f(alpha) is large (clear path)
            # and when angle_diff_candidate_to_Oi is small (aligned with destination).
            cost = (self.d_max_collision_dist**2) + (f_alpha**2) - \
                   2 * self.d_max_collision_dist * f_alpha * np.cos(angle_diff_candidate_to_Oi)

            # Heavily penalize directions that lead to immediate collision
            if f_alpha < self.size * 0.75 : # If collision distance is very small
                cost += 10000 * (self.size * 0.75 - f_alpha)


            if cost < best_cost:
                best_cost = cost
                chosen_direction_vector = np.array([np.cos(candidate_world_angle), np.sin(candidate_world_angle)])
        
        return chosen_direction_vector

    def update_behavior(self, static_obstacles, other_pedestrians, width, height):
        if self.is_arrived:
            self.velocity *= 0.8 
            if np.linalg.norm(self.velocity) < 0.1 : self.velocity = np.zeros(2)
            self.acceleration = np.zeros(2)
            return

        best_dir_vec = self._calculate_best_direction_vector(static_obstacles, other_pedestrians)

        if np.linalg.norm(best_dir_vec) < 0.01: 
            steering_force = -self.velocity * 0.1 
        else:
            desired_velocity = best_dir_vec * self.max_speed
            steering_force = desired_velocity - self.velocity
        
        steering_force = limit_vector(steering_force, self.max_force)
        self.apply_force(steering_force)

    # display method can be inherited from Agent or overridden if specific visuals are needed
    # For example, to draw the FOV or destination:
    def display(self, ax):
        super().display(ax) # Draw agent body and history trail
        # Optionally draw destination
        if not self.is_arrived:
             ax.plot([self.position[0], self.destination[0]], 
                     [self.position[1], self.destination[1]], 
                     color=self.color, linestyle=':', alpha=0.2, linewidth=0.8)
        
        # Determine current forward angle for FOV visualization
        current_forward_angle_deg = 0
        if np.linalg.norm(self.velocity) > 0.01:
            current_forward_angle_rad = np.arctan2(self.velocity[1], self.velocity[0])
            current_forward_angle_deg = np.degrees(current_forward_angle_rad)
        else: # If not moving, FOV might be based on direction to destination or a default
            vec_to_dest = self.destination - self.position
            if np.linalg.norm(vec_to_dest) > 0.1:
               current_forward_angle_rad = np.arctan2(vec_to_dest[1], vec_to_dest[0])
               current_forward_angle_deg = np.degrees(current_forward_angle_rad)
            # else: current_forward_angle_deg remains 0 (default forward if no motion and at/near dest)

        fov_radius_visual = self.d_max_collision_dist * 0.6 # Visual radius of the FOV wedge
        
        # Angles for the Wedge patch are in degrees
        # self.fov_radians is half of the total FOV angle
        half_fov_deg = np.degrees(self.fov_radians)
        
        # theta1 is the start angle, theta2 is the end angle of the wedge
        theta1 = current_forward_angle_deg - half_fov_deg
        theta2 = current_forward_angle_deg + half_fov_deg
        
        # Create and add the Wedge patch for FOV
        fov_wedge = plt.matplotlib.patches.Wedge(
            center=self.position,
            r=fov_radius_visual,
            theta1=theta1,
            theta2=theta2,
            color='gray', # Color of the FOV wedge
            alpha=0.15    # Transparency of the FOV wedge
        )
        ax.add_patch(fov_wedge)
