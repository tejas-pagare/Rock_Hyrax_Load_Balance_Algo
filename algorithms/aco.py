import numpy as np
from .base import LoadBalancer

class AntColonyBalancer(LoadBalancer):
    """
    Implements an Ant Colony Optimization (ACO) algorithm for load balancing.
    """
    def __init__(self, vms, alpha=1.0, beta=2.0, evap_rate=0.1):
        super().__init__(vms)
        self.alpha = alpha       # Pheromone importance
        self.beta = beta         # Heuristic importance
        self.evap_rate = evap_rate # Pheromone evaporation rate
        self.pheromones = np.ones(self.num_vms) # Initialize all trails
    
    def assign_task(self, task, log_tasks=False):
        """Assigns a task using online ACO logic."""
        
        # 1. Get Heuristic (Eta) - lower EFT is better, so eta = 1/EFT
        efts = self._get_expected_finish_times(task)
        # Add small epsilon to avoid division by zero
        eta = 1.0 / (efts + 1e-6)
        
        # 2. Calculate Probabilities
        # (tau^alpha) * (eta^beta)
        attractions = (self.pheromones ** self.alpha) * (eta ** self.beta)
        
        # Handle case where all attractions are zero
        if np.sum(attractions) == 0:
            probabilities = np.ones(self.num_vms) / self.num_vms
        else:
            probabilities = attractions / np.sum(attractions)
        
        # 3. Choose VM based on probability (Roulette Wheel)
        chosen_vm_id = np.random.choice(self.num_vms, p=probabilities)
        
        # --- Logging ---
        if log_tasks and len(self.log) < 50:
            log_msg = f"Task {task['id']}: Chose VM {chosen_vm_id} (Prob: {probabilities[chosen_vm_id]:.3f})"
            self.log.append(log_msg)
        
        # --- Task Metrics ---
        task_finish_time = efts[chosen_vm_id]
        self.task_log.append({"response_time": task_finish_time})

        # 4. Assign task
        self.vm_loads[chosen_vm_id] += task['length']

        # 5. Update Pheromones
        # a. Evaporation
        self.pheromones *= (1 - self.evap_rate)
        
        # b. Deposit
        # Deposit is inverse of task finish time - better (faster) time = more deposit
        deposit_amount = 1.0 / (task_finish_time + 1e-6)
        self.pheromones[chosen_vm_id] += deposit_amount

    def simulate(self, tasks, log_tasks=False):
        """Runs the ACO simulation for all tasks."""
        self.reset()
        # Reset pheromones for a fresh simulation
        self.pheromones = np.ones(self.num_vms)
        for task in tasks:
            self.assign_task(task, log_tasks)
        return self.get_vm_finish_times()