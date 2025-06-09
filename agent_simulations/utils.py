import numpy as np
import matplotlib.pyplot as plt

def limit_vector(vector, max_val):
    """Limits the magnitude of a vector."""
    mag = np.linalg.norm(vector)
    if mag > max_val:
        vector = (vector / mag) * max_val
    return vector

def normalize_vector(vector):
    """Normalizes a vector, returns zero vector if magnitude is zero."""
    mag = np.linalg.norm(vector)
    if mag > 0:
        return vector / mag
    return np.zeros_like(vector)

def setup_plot(width, height, title):
    """Sets up the matplotlib plot for animation."""
    fig, ax = plt.subplots()
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title(title)
    return fig, ax
