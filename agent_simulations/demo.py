'''
Demo for the Pedestrian model.
'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import numpy as np

from utils import setup_plot
from boid import Boid
from pedestrian import Pedestrian
from actors import Evader, Pursuer
from config import *

WIDTH = GENERAL_CONFIG['width']
HEIGHT = GENERAL_CONFIG['height']

def run_boids_demo():
    fig, ax = setup_plot(WIDTH, HEIGHT, "6.1 Boids Model Demo")
    
    num_boids = BOIDS_CONFIG['num_agents']
    boids = [Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), 
                  max_speed=BOIDS_CONFIG['max_speed'], 
                  max_force=BOIDS_CONFIG['max_force'], 
                  perception_radius=BOIDS_CONFIG['perception_radius'],
                  sep_factor=BOIDS_CONFIG['separation_factor'], 
                  ali_factor=BOIDS_CONFIG['alignment_factor'], 
                  coh_factor=BOIDS_CONFIG['cohesion_factor']) 
             for _ in range(num_boids)]

    def update_boids(frame):
        ax.clear()
        ax.set_xlim(0, WIDTH)
        ax.set_ylim(0, HEIGHT)
        ax.set_facecolor(BOIDS_CONFIG['background_color'])
        
        for boid in boids:
            boid.flock(boids)
            boid.update()
            boid.edges(WIDTH, HEIGHT)
            boid.display(ax)
        # Return a list of artists to be redrawn for blitting
        return ax.patches + ax.lines 

    # Use blit=True for smoother animation if possible, requires update function to return artists
    ani = animation.FuncAnimation(fig, update_boids, 
                                frames=GENERAL_CONFIG['animation_frames'], 
                                interval=GENERAL_CONFIG['animation_interval'], 
                                blit=True)
    plt.show()

def run_pedestrian_demo():
    fig, ax = setup_plot(WIDTH, HEIGHT, "6.2 Pedestrian Model with Obstacles and FOV Demo") # Updated title
    
    cfg = PEDESTRIAN_CONFIG
    num_pedestrians = cfg['num_agents']
    
    pedestrians = []

    def create_random_destination(current_pos, min_dist=WIDTH/4): # Ensure destination is reasonably far
        """Creates a random destination sufficiently far from current_pos."""
        while True:
            dest = np.random.rand(2) * [WIDTH, HEIGHT]
            if np.linalg.norm(dest - current_pos) > min_dist:
                return dest

    for _ in range(num_pedestrians):
        start_pos = np.random.rand(2) * [WIDTH, HEIGHT]
        destination = create_random_destination(start_pos)
        ped = Pedestrian(start_pos[0], start_pos[1],
                         max_speed=cfg['max_speed'], 
                         max_force=cfg['max_force'],
                         destination=destination, # Pass destination
                         fov_degrees=cfg['fov_degrees'],
                         d_max_collision_dist=cfg['d_max_collision_dist'],
                         num_fov_samples=cfg['num_fov_samples'],
                         arrival_threshold=cfg['arrival_threshold'],
                         size=random.uniform(6,9)) 
        pedestrians.append(ped)

    # Create static obstacles based on config
    static_obstacles_cfg = cfg['obstacle_settings']
    static_obstacles = []
    for _ in range(static_obstacles_cfg['num_static_obstacles']):
        # Ensure obstacles are not too close to edges initially
        obs_pos = np.random.rand(2) * [WIDTH * 0.8, HEIGHT * 0.8] + [WIDTH * 0.1, HEIGHT * 0.1] 
        obs_radius = random.uniform(static_obstacles_cfg['min_radius'], static_obstacles_cfg['max_radius'])
        static_obstacles.append({'position': obs_pos, 'radius': obs_radius, 'color': static_obstacles_cfg['color']})

    # Create patches for obstacles for efficient drawing if they don't change
    obstacle_patches = [plt.Circle(obs['position'], obs['radius'], color=obs['color'], alpha=0.7) for obs in static_obstacles]
    
    def update_pedestrians(frame):
        ax.clear()
        ax.set_xlim(0, WIDTH)
        ax.set_ylim(0, HEIGHT)
        ax.set_facecolor(cfg.get('background_color', (0.9, 0.9, 0.88))) # Use get for safety

        # Draw static obstacles
        for patch in obstacle_patches:
            # ax.add_patch(patch) # This creates new patches every frame, leading to memory issues with blit=True
            # Instead, if patches are static, they should ideally be drawn once or handled carefully with blitting.
            # For simplicity without complex blitting management of static artists:
            ax.add_artist(plt.Circle(patch.center, patch.radius, color=patch.get_facecolor(), alpha=patch.get_alpha()))


        all_ped_objects = list(pedestrians) 

        for i, p in enumerate(pedestrians):
            other_peds_for_current = all_ped_objects[:i] + all_ped_objects[i+1:]
            
            p.update_behavior(static_obstacles, other_peds_for_current, WIDTH, HEIGHT)
            p.update()
            p.edges(WIDTH, HEIGHT) 
            p.display(ax)

            if p.is_arrived:
                p.destination = create_random_destination(p.position)
                p.is_arrived = False
        
        # Return all artists that need to be redrawn for blitting
        # This includes agent bodies, history trails, and potentially FOV lines/destination lines if drawn by display()
        drawn_artists = []
        for p_artist in ax.patches: # Agent bodies are patches
            drawn_artists.append(p_artist)
        for l_artist in ax.lines: # History trails, destination lines are lines
            drawn_artists.append(l_artist)
        # Obstacles are already handled by re-adding them as artists above for non-blit or simple blit.
        # If true blitting with static elements is desired, a more complex setup is needed.
        return drawn_artists


    ani = animation.FuncAnimation(fig, update_pedestrians, 
                                frames=GENERAL_CONFIG['animation_frames'] + 50, # More frames for observation
                                interval=GENERAL_CONFIG['animation_interval'] + 20, # Slightly slower interval
                                blit=True) # blit=True requires the update function to return a list of artists
    plt.show()

def run_pursuit_evasion_demo():
    fig, ax = setup_plot(WIDTH, HEIGHT, "6.3 Multi-Robot Pursuit-Evasion Demo")
    
    evader_config = PURSUIT_EVASION_CONFIG['evader']
    evader = Evader(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), 
                    max_speed=evader_config['max_speed'], 
                    max_force=evader_config['max_force'],
                    flee_radius=evader_config['flee_radius'])
    
    pursuer_config = PURSUIT_EVASION_CONFIG['pursuer']
    num_pursuers = pursuer_config['num_agents']
    pursuers = [Pursuer(random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                        max_speed=pursuer_config['max_speed'], 
                        max_force=pursuer_config['max_force'])
                for _ in range(num_pursuers)]

    def update_pursuit_evasion(frame):
        ax.clear()
        ax.set_xlim(0, WIDTH)
        ax.set_ylim(0, HEIGHT)
        ax.set_facecolor(PURSUIT_EVASION_CONFIG['background_color'])

        evader.update_behavior(pursuers) 
        evader.update()
        evader.edges(WIDTH, HEIGHT)
        evader.display(ax)

        for p in pursuers:
            p.update_behavior(evader) 
            p.update()
            p.edges(WIDTH, HEIGHT)
            p.display(ax)
            if np.linalg.norm(p.position - evader.position) < p.size + evader.size + 10: 
                 ax.plot([p.position[0], evader.position[0]], 
                         [p.position[1], evader.position[1]], 
                         'yellow', linestyle='--', linewidth=0.7, alpha=0.5)

        return ax.patches + ax.lines

    ani = animation.FuncAnimation(fig, update_pursuit_evasion, 
                                frames=GENERAL_CONFIG['animation_frames'], 
                                interval=GENERAL_CONFIG['animation_interval'], 
                                blit=True)
    plt.show()

if __name__ == '__main__':
    run_pedestrian_demo()
