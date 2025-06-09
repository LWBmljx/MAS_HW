import random

class SIRModel:
    def __init__(self, graph, infection_prob, recovery_prob, susceptible_state, infected_state, recovered_state):
        self.graph = graph.copy()
        self.nodes = list(self.graph.nodes())
        self.num_nodes = len(self.nodes)

        self.infection_prob = infection_prob
        self.recovery_prob = recovery_prob

        # Define states using provided constants
        self.SUSCEPTIBLE = susceptible_state
        self.INFECTED = infected_state
        self.RECOVERED = recovered_state

        # Initialize all nodes to susceptible
        self.states = {node: self.SUSCEPTIBLE for node in self.nodes}
        
        # Keep track of S, I, R counts over time
        self.s_counts = [self.num_nodes]
        self.i_counts = [0]
        self.r_counts = [0]
        self.timesteps = [0]

    def set_initial_infected_nodes(self, initial_infected_nodes):
        """Sets the initial set of infected nodes."""
        for node in initial_infected_nodes:
            if node in self.states and self.states[node] == self.SUSCEPTIBLE:
                self.states[node] = self.INFECTED
            else:
                print(f"Warning: Node {node} not in graph or not susceptible, cannot infect initially.")
        self._update_counts(0) # Update counts after initial infection

    def _update_counts(self, current_time_step):
        s = sum(1 for node in self.nodes if self.states[node] == self.SUSCEPTIBLE)
        i = sum(1 for node in self.nodes if self.states[node] == self.INFECTED)
        r = sum(1 for node in self.nodes if self.states[node] == self.RECOVERED)
        
        if self.timesteps[-1] == current_time_step:
            self.s_counts[-1] = s
            self.i_counts[-1] = i
            self.r_counts[-1] = r
        else:
            self.s_counts.append(s)
            self.i_counts.append(i)
            self.r_counts.append(r)
            self.timesteps.append(current_time_step)

    def step(self, current_time_step):
        """Performs a single step of the epidemic spread."""
        newly_infected_this_step = []
        newly_recovered_this_step = []

        for node in self.nodes:
            if self.states[node] == self.INFECTED:
                # Attempt to recover
                if random.random() < self.recovery_prob:
                    newly_recovered_this_step.append(node)
                else:
                    # Attempt to infect neighbors
                    for neighbor in self.graph.neighbors(node):
                        if self.states[neighbor] == self.SUSCEPTIBLE:
                            if random.random() < self.infection_prob:
                                # Check if already set to be infected in this step to avoid double processing
                                if neighbor not in newly_infected_this_step: 
                                    newly_infected_this_step.append(neighbor)
        
        # Apply changes for this step
        for node in newly_infected_this_step:
            self.states[node] = self.INFECTED
        
        for node in newly_recovered_this_step:
            self.states[node] = self.RECOVERED
        
        self._update_counts(current_time_step)
        return len(newly_infected_this_step), len(newly_recovered_this_step)

    def run(self, max_steps=100):
        """Runs the simulation until no more infected nodes or max_steps is reached."""
        for t in range(1, max_steps + 1):
            num_infected, num_recovered = self.step(t)
            if self.i_counts[-1] == 0 and t > 1: # Epidemic died out
                break
        return self.s_counts, self.i_counts, self.r_counts, self.timesteps

    def get_current_states(self):
        return self.states.copy()
