import random

class LinearThresholdModel:
    def __init__(self, graph, thresholds=None):
        self.graph = graph.copy() # Work on a copy
        self.nodes = list(self.graph.nodes())
        self.num_nodes = len(self.nodes)

        # Initialize states: 0 for inactive, 1 for active
        self.states = {node: 0 for node in self.nodes}

        # Initialize thresholds
        if thresholds:
            self.thresholds = thresholds
        else:
            # Assign random thresholds between 0 and 1 if not provided
            self.thresholds = {node: random.uniform(0.01, 0.5) for node in self.nodes}

        # Initialize influence weights (typically 1/in-degree for unweighted graphs)
        # For simplicity, let's assume unweighted influence from neighbors
        # More complex models might assign specific weights to edges
        self.weights = {}
        for node in self.graph.nodes():
            neighbors = list(self.graph.predecessors(node)) # In-neighbors for directed graph
            if not neighbors: # Handle nodes with no in-neighbors
                self.weights[node] = {}
                continue
            # Default: equal weight from each active neighbor
            # More sophisticated: weight w_ij from neighbor j to i
            # For now, let's consider the influence of an active neighbor to be 1
            # The sum of influences will be the count of active neighbors
            # A common approach is to normalize weights such that sum of incoming weights is <= 1
            # Here, we'll use a simpler interpretation: influence = count of active neighbors / degree
            # Or, each neighbor contributes a fixed influence if the graph is unweighted.
            # Let's use a model where each active neighbor contributes an influence, and this is summed.
            # The threshold is compared against this sum.
            # For this example, let's assume each active neighbor contributes an influence of (1 / in_degree)
            # if in_degree > 0, else 0.
            in_degree = self.graph.in_degree(node)
            if in_degree > 0:
                 # each incoming edge has a weight, for now, let's assume they are uniform
                 # or specified in the graph. If not specified, use 1/in_degree.
                for neighbor in neighbors:
                    if self.graph.has_edge(neighbor, node) and 'weight' in self.graph[neighbor][node]:
                        self.weights.setdefault(node, {})[neighbor] = self.graph[neighbor][node]['weight']
                    else:
                        self.weights.setdefault(node, {})[neighbor] = 1.0 / in_degree # Default if no weight
            else:
                self.weights[node] = {}


    def set_initial_active_nodes(self, initial_active_nodes):
        """Sets the initial set of active nodes."""
        for node in initial_active_nodes:
            if node in self.states:
                self.states[node] = 1
            else:
                print(f"Warning: Node {node} not in graph, cannot activate.")

    def step(self):
        """Performs a single step of the influence propagation."""
        newly_activated_count = 0
        # Nodes that will be activated in this step, to avoid cascading effect within one step
        to_activate_in_this_step = []

        for node in self.nodes:
            if self.states[node] == 1:  # Already active
                continue

            # Calculate the total influence from active neighbors
            total_influence = 0
            for neighbor in self.graph.predecessors(node): # Consider in-neighbors
                if self.states[neighbor] == 1:
                    total_influence += self.weights[node].get(neighbor, 0) # Use pre-calculated weights
            
            if total_influence >= self.thresholds[node]:
                to_activate_in_this_step.append(node)
        
        for node in to_activate_in_this_step:
            if self.states[node] == 0: # Ensure it wasn't activated by another path in a more complex step logic
                self.states[node] = 1
                newly_activated_count += 1
        
        return newly_activated_count

    def run(self, max_steps=100):
        """Runs the simulation until no more nodes can be activated or max_steps is reached."""
        history = [self.states.copy()]
        for _ in range(max_steps):
            activated_in_step = self.step()
            history.append(self.states.copy())
            if activated_in_step == 0: # No more nodes were activated
                break
        return history

    def get_active_nodes(self):
        return [node for node, state in self.states.items() if state == 1]
