\
import matplotlib
matplotlib.use('TkAgg')  # Set backend to avoid Qt issues
import matplotlib.pyplot as plt
import networkx as nx

def setup_plot(title, figsize=(8, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    return fig, ax

def draw_network(graph, states, pos, ax, config, node_size=300, with_labels=False):
    ax.clear()
    
    # Define colors based on the model type implicitly through config
    if 'threshold' in config: # Linear Threshold Model
        colors = [config['colors']['active'] if states[node] == 1 else config['colors']['inactive'] for node in graph.nodes()]
    elif 'infection_prob' in config: # Epidemic Model (SIR)
        color_map = {
            config['states']['susceptible']: config['colors']['susceptible'],
            config['states']['infected']: config['colors']['infected'],
            config['states']['recovered']: config['colors']['recovered']
        }
        colors = [color_map[states[node]] for node in graph.nodes()]
    else:
        colors = ['skyblue'] * len(graph.nodes())


    nx.draw(graph, pos, ax=ax, node_color=colors, node_size=node_size, 
            with_labels=with_labels, width=0.5, alpha=0.8)
    ax.set_title(ax.get_title()) # Keep original title after clear

def plot_sir_counts(timesteps, s_counts, i_counts, r_counts, ax_counts, title="SIR Model Dynamics"):
    ax_counts.clear()
    ax_counts.plot(timesteps, s_counts, label='Susceptible', color='blue')
    ax_counts.plot(timesteps, i_counts, label='Infected', color='red')
    ax_counts.plot(timesteps, r_counts, label='Recovered', color='green')
    ax_counts.set_xlabel("Time Steps")
    ax_counts.set_ylabel("Number of Nodes")
    ax_counts.legend()
    ax_counts.set_title(title)
    ax_counts.grid(True)
