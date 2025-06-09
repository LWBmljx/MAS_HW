'''
Configuration settings for all network model simulations.
'''

GENERAL_CONFIG = {
    'width_pixels': 800,  # For plot window size
    'height_pixels': 700, # For plot window size (SIR demo needs more height)
    'animation_interval_ms': 200, 
    'random_seed': 42,      # For reproducibility of graph layouts and random choices
}

LT_MODEL_CONFIG = {
    'num_nodes': 10,
    # 'connection_prob': 0.1, # For Erdos-Renyi graph
    'barabasi_m': 2,        # For Barabasi-Albert graph (m edges to add for each new node)
    'num_initial_active': 1,
    'default_threshold': 0.2, # Default threshold if not randomly assigned
    'max_simulation_steps': 50,
    'extra_frames_at_end': 5, # To see the final state a bit longer
    'node_size': 250,
    'colors': {
        'inactive': 'lightblue',
        'active': 'red'
    },
    'threshold': True # Marker for utils.draw_network to identify this model type
}

SIR_MODEL_CONFIG = {
    'num_nodes': 100,
    # 'connection_prob': 0.08, # For Erdos-Renyi graph
    'barabasi_m': 2,         # For Barabasi-Albert graph
    'num_initial_infected': 2,
    'infection_prob': 0.15,   # Probability of an infected node infecting a susceptible neighbor
    'recovery_prob': 0.05,   # Probability of an infected node recovering
    'max_simulation_steps': 150,
    'extra_frames_at_end': 10,
    'node_size': 200,
    'states': { # Define state constants for clarity
        'susceptible': 'S',
        'infected': 'I',
        'recovered': 'R'
    },
    'colors': {
        'susceptible': 'blue',
        'infected': 'red',
        'recovered': 'green'
    },
    'infection_prob': True # Marker for utils.draw_network to identify this model type (using a key that exists)
}
