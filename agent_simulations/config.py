GENERAL_CONFIG = {
    'width': 800,
    'height': 600,
    'animation_frames': 200, 
    'animation_interval': 1, 
}

BOIDS_CONFIG = {
    'num_agents': 100,
    'max_speed': 3.0,
    'max_force': 0.1,
    'perception_radius': 70.0,
    'separation_factor': 1.2,
    'alignment_factor': 1.0,
    'cohesion_factor': 1.2,
    'background_color': 'black',
}

PEDESTRIAN_CONFIG = {
    'num_agents': 30,
    'max_speed': 1.3,
    'max_force': 0.35,
    'fov_degrees': 150,         
    'd_max_collision_dist': 70, 
    'num_fov_samples': 25,      
    'arrival_threshold': 8.0,   
    'background_color': (0.92, 0.92, 0.88),
    'obstacle_settings': {
        'num_static_obstacles': 5,
        'min_radius': 10,
        'max_radius': 18,
        'color': 'gray'
    }
}

PURSUIT_EVASION_CONFIG = {
    'evader': {
        'max_speed': 2.8, 
        'max_force': 0.35,
        'flee_radius': 200.0,
    },
    'pursuer': {
        'num_agents': 3,
        'max_speed': 3.5,
        'max_force': 0.4,
    },
    'background_color': (0.1, 0.1, 0.2), 
}
