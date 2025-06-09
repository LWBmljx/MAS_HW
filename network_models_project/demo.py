import networkx as nx
import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec

from utils import setup_plot, draw_network, plot_sir_counts
from sir_model import SIRModel
from lt_model import LinearThresholdModel
from config import *

WIDTH_PIXELS = GENERAL_CONFIG['width_pixels']
HEIGHT_PIXELS = GENERAL_CONFIG['height_pixels']

def run_sir_model_demo():
    # graph = nx.erdos_renyi_graph(n=SIR_MODEL_CONFIG['num_nodes'], p=SIR_MODEL_CONFIG['connection_prob'], seed=GENERAL_CONFIG['random_seed'])
    graph = nx.barabasi_albert_graph(n=SIR_MODEL_CONFIG['num_nodes'], m=SIR_MODEL_CONFIG['barabasi_m'], seed=GENERAL_CONFIG['random_seed'])
    pos = nx.spring_layout(graph, seed=GENERAL_CONFIG['random_seed'])

    model = SIRModel(graph, 
                     infection_prob=SIR_MODEL_CONFIG['infection_prob'], 
                     recovery_prob=SIR_MODEL_CONFIG['recovery_prob'],
                     susceptible_state=SIR_MODEL_CONFIG['states']['susceptible'],
                     infected_state=SIR_MODEL_CONFIG['states']['infected'],
                     recovered_state=SIR_MODEL_CONFIG['states']['recovered'])

    num_initial_infected = SIR_MODEL_CONFIG['num_initial_infected']
    if num_initial_infected > 0 and len(graph.nodes()) > 0:
        initial_infected_nodes = random.sample(list(graph.nodes()), k=min(num_initial_infected, len(graph.nodes())))
        model.set_initial_infected_nodes(initial_infected_nodes)
    else:
        initial_infected_nodes = [] # Should still call set_initial_infected_nodes to init counts
        model.set_initial_infected_nodes([])

    fig = plt.figure(figsize=(WIDTH_PIXELS/100, HEIGHT_PIXELS/80)) # Adjusted figure size
    gs = GridSpec(2, 1, height_ratios=[3, 1]) # 2 rows, 1 column. Network gets 3/4, SIR plot 1/4
    ax_network = fig.add_subplot(gs[0])
    ax_sir_plot = fig.add_subplot(gs[1])
    
    ax_network.set_title("5.3 SIR Epidemic Model Demo")
    ax_network.set_xticks([])
    ax_network.set_yticks([])
    plt.tight_layout(pad=3.0)

    simulation_step = 0
    max_steps = SIR_MODEL_CONFIG['max_simulation_steps']

    def update_frame(frame_num):
        nonlocal simulation_step
        
        if simulation_step < max_steps and model.i_counts[-1] > 0:
            num_newly_infected, num_newly_recovered = model.step(simulation_step + 1)
            current_states = model.get_current_states()
            draw_network(model.graph, current_states, pos, ax_network, SIR_MODEL_CONFIG, node_size=SIR_MODEL_CONFIG['node_size'])
            ax_network.set_title(f"SIR Model - Step: {simulation_step + 1} (New Infected: {num_newly_infected}, New Recovered: {num_newly_recovered})")
            simulation_step += 1
        elif simulation_step >= max_steps:
            ax_network.set_title(f"SIR Model - Step: {simulation_step} (Max steps reached)")
        elif model.i_counts[-1] == 0 and simulation_step > 0:
            ax_network.set_title(f"SIR Model - Step: {simulation_step} (Epidemic ended)")
            # ani.event_source.stop() # Stop animation if epidemic ends

        # Always draw the network and SIR plot, even if simulation step doesn't advance
        current_states = model.get_current_states()
        draw_network(model.graph, current_states, pos, ax_network, SIR_MODEL_CONFIG, node_size=SIR_MODEL_CONFIG['node_size'])
        plot_sir_counts(model.timesteps, model.s_counts, model.i_counts, model.r_counts, ax_sir_plot)
        
        # Return a list of artists for blitting (if used, though can be complex with subplots)
        # For simplicity with subplots, blit=False is often easier.
        # return list(ax_network.patches) + list(ax_network.lines) + list(ax_sir_plot.lines)
        return # Return nothing if blit=False

    ani = animation.FuncAnimation(fig, update_frame, 
                                frames=max_steps + SIR_MODEL_CONFIG['extra_frames_at_end'], 
                                interval=GENERAL_CONFIG['animation_interval_ms'], 
                                repeat=False, blit=False)
    plt.show()

def run_lt_model_demo():
    graph = nx.barabasi_albert_graph(n=LT_MODEL_CONFIG['num_nodes'], m=LT_MODEL_CONFIG['barabasi_m'], seed=GENERAL_CONFIG['random_seed'])
    graph = nx.DiGraph(graph) # Ensure it's directed for LT model's predecessor logic

    pos = nx.spring_layout(graph, seed=GENERAL_CONFIG['random_seed'])

    thresholds = {node: LT_MODEL_CONFIG['default_threshold'] for node in graph.nodes()}
    # thresholds = {node: random.uniform(0.1, 0.4) for node in graph.nodes()} # Alternative: random thresholds
    
    model = LinearThresholdModel(graph, thresholds=thresholds)

    num_initial_active = LT_MODEL_CONFIG['num_initial_active']
    if num_initial_active > 0 and len(graph.nodes()) > 0:
        initial_active_nodes = random.sample(list(graph.nodes()), k=min(num_initial_active, len(graph.nodes())))
        model.set_initial_active_nodes(initial_active_nodes)
    else:
        initial_active_nodes = []

    # Prepare edge weight labels
    edge_weight_labels = {}
    for node, incoming_edges in model.weights.items():
        for neighbor, weight in incoming_edges.items():
            if model.graph.has_edge(neighbor, node): # Ensure edge exists in the graph copy
                edge_weight_labels[(neighbor, node)] = f"{weight:.2f}"

    # Prepare node threshold labels
    node_threshold_labels = {node: f"{model.thresholds[node]:.2f}" for node in model.graph.nodes()}

    current_states = model.states.copy()
    simulation_step = 0
    max_steps = LT_MODEL_CONFIG['max_simulation_steps']

    fig, ax = setup_plot("5.2 Linear Threshold Model Demo", figsize=(WIDTH_PIXELS/100, HEIGHT_PIXELS/100))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05)

    def update_frame(frame_num):
        time.sleep(1)
        nonlocal simulation_step, current_states
        ax.clear() # Clear previous frame

        if simulation_step < max_steps:
            activated_count = model.step() # Advances model.states
            current_states = model.states.copy()
            draw_network(model.graph, current_states, pos, ax, LT_MODEL_CONFIG, node_size=LT_MODEL_CONFIG['node_size'])
            
            # Draw edge weights
            nx.draw_networkx_edge_labels(model.graph, pos, edge_labels=edge_weight_labels, ax=ax, font_size=7, font_color='blue', rotate=False)
            
            # Draw node thresholds (as labels)
            # Adjust label_pos for better visibility if needed, e.g., slightly offset from node center
            label_pos = {k: [v[0], v[1] + 0.035] for k, v in pos.items()} # Offset labels slightly above nodes
            nx.draw_networkx_labels(model.graph, label_pos, labels=node_threshold_labels, ax=ax, font_size=8, font_color='green')

            ax.set_title(f"Linear Threshold Model - Step: {simulation_step + 1} (Activated this step: {activated_count})")
            simulation_step += 1
            if activated_count == 0 and simulation_step > 1: # Stable state
                ax.text(0.5, -0.02, "Network has stabilized.", ha='center', va='top', transform=ax.transAxes, fontsize=10, color='red')
                # ani.event_source.stop() # Stop animation if stable - requires 'ani' to be defined
        else: # Max steps reached or simulation ended before this logic path
            draw_network(model.graph, current_states, pos, ax, LT_MODEL_CONFIG, node_size=LT_MODEL_CONFIG['node_size'])
            # Also draw labels in the final state
            nx.draw_networkx_edge_labels(model.graph, pos, edge_labels=edge_weight_labels, ax=ax, font_size=7, font_color='blue', rotate=False)
            label_pos = {k: [v[0], v[1] + 0.035] for k, v in pos.items()}
            nx.draw_networkx_labels(model.graph, label_pos, labels=node_threshold_labels, ax=ax, font_size=8, font_color='green')
            ax.set_title(f"Linear Threshold Model - Step: {simulation_step} (Max steps reached or stable)")
            # ani.event_source.stop()

        # Ensure axes limits are maintained if necessary, though ax.clear() and redraw usually handles this.
        ax.set_xticks([])
        ax.set_yticks([])
        return ax.patches + ax.lines # For blitting if used, though blitting with networkx can be tricky

    ani = animation.FuncAnimation(fig, update_frame, 
                                frames=max_steps + LT_MODEL_CONFIG['extra_frames_at_end'], 
                                interval=GENERAL_CONFIG['animation_interval_ms'], 
                                repeat=False, blit=False) 
    plt.show()