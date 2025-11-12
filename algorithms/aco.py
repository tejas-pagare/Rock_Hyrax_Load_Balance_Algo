import numpy as np
from .base import LoadBalancer

class AntColonyBalancer(LoadBalancer):
    """
    Implements an Ant Colony Optimization (ACO) algorithm for load balancing.
    """
    def __init__(self, vms, alpha=1.0, beta=2.0, evap_rate=0.1, q0=0.0, tau_min=1e-3, tau_max=10.0):
        super().__init__(vms)
        self.alpha = alpha          # Pheromone importance
        self.beta = beta            # Heuristic importance
        self.evap_rate = evap_rate  # Pheromone evaporation rate per task
        self.q0 = q0                # Greedy selection probability (ACS style)
        self.tau_min = tau_min      # Lower pheromone bound
        self.tau_max = tau_max      # Upper pheromone bound
        # Initialize trails in the middle of bounds
        init_tau = min(max(1.0, tau_min), tau_max)
        self.pheromones = np.full(self.num_vms, init_tau, dtype=float)
    
    def assign_task(self, task, log_tasks=False):
        """Assigns a task using online ACO logic."""
        
        # 1. Get Heuristic (Eta) - lower EFT is better, so eta = 1/EFT
        efts = self._get_expected_finish_times(task)
        # Add small epsilon to avoid division by zero
        eta = 1.0 / (efts + 1e-6)
        
        # 2. Compute attractions and choose VM (ACS rule)
        attractions = (self.pheromones ** self.alpha) * (eta ** self.beta)
        sum_attr = np.sum(attractions)
        if sum_attr <= 0 or not np.isfinite(sum_attr):
            probabilities = np.ones(self.num_vms) / self.num_vms
        else:
            probabilities = attractions / sum_attr

        if np.random.rand() < self.q0:
            # Greedy pick best attraction
            chosen_vm_id = int(np.argmax(attractions))
        else:
            # Roulette wheel sampling
            chosen_vm_id = int(np.random.choice(self.num_vms, p=probabilities))
        
        # --- Logging ---
        if log_tasks and len(self.log) < 50:
            prob_str = probabilities[chosen_vm_id] if 'probabilities' in locals() else 1.0/self.num_vms
            log_msg = f"Task {task['id']}: Chose VM {chosen_vm_id} (Prob: {prob_str:.3f})"
            self.log.append(log_msg)
        
        # --- Task Metrics ---
        task_finish_time = efts[chosen_vm_id]
        self.task_log.append({"response_time": task_finish_time})
        # 4. Assign task
        self.vm_loads[chosen_vm_id] += task['length']

        # 5. Update Pheromones
        # a. Evaporation (element-wise) with lower bound
        self.pheromones *= (1 - self.evap_rate)
        self.pheromones = np.clip(self.pheromones, self.tau_min, self.tau_max)
        
        # b. Deposit on chosen VM; scale by inverse time
        deposit_amount = 1.0 / (task_finish_time + 1e-6)
        self.pheromones[chosen_vm_id] = np.clip(
            self.pheromones[chosen_vm_id] + deposit_amount,
            self.tau_min,
            self.tau_max
        )

        # Return selected VM id for external simulators (e.g., SimPy)
        return chosen_vm_id

    def simulate(self, tasks, log_tasks=False):
        """Runs the ACO simulation for all tasks."""
        self.reset()
        # Reset pheromones for a fresh simulation
        self.pheromones = np.ones(self.num_vms)
        for task in tasks:
            self.assign_task(task, log_tasks)
        return self.get_vm_finish_times()