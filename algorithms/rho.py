import random
import numpy as np
from .base import LoadBalancer

class RockHyraxBalancer(LoadBalancer):
    """
    Implements the Rock Hyrax Optimization (RHO) load balancing algorithm.
    """
    def __init__(self, vms, w1=0.7, w2=0.3):
        super().__init__(vms)
        self.w1 = w1 # Weight for time (Makespan/Response)
        self.w2 = w2 # Weight for energy

    def _get_fitness_scores(self, task):
        """
        Calculates the fitness for all VMs based on the paper's
        multi-objective approach (Eq. 5).
        
        Fitness = w1 * Time_Cost + w2 * Energy_Cost
        """
        fitness_scores = np.zeros(self.num_vms)
        
        # 1. Calculate raw costs
        raw_time_costs = self._get_expected_finish_times(task)
        raw_energy_costs = np.zeros(self.num_vms)
        
        for i in range(self.num_vms):
            vm = self.vms[i]
            if vm["mips"] > 0:
                raw_energy_costs[i] = vm["p_max"]
            else:
                raw_energy_costs[i] = float('inf')

        # 2. Normalize costs (min-max scaling) to be in [0, 1]
        min_time, max_time = np.min(raw_time_costs), np.max(raw_time_costs)
        min_energy, max_energy = np.min(raw_energy_costs), np.max(raw_energy_costs)

        norm_time = (raw_time_costs - min_time) / (max_time - min_time + 1e-6)
        norm_energy = (raw_energy_costs - min_energy) / (max_energy - min_energy + 1e-6)
        
        # 3. Calculate final fitness (lower is better)
        for i in range(self.num_vms):
            fitness_scores[i] = (self.w1 * norm_time[i]) + (self.w2 * norm_energy[i])
            
        return fitness_scores

    def assign_task(self, task, log_tasks=False):
        """
        Assigns a single task using the RHO logic (Phases 1 and 2).
        """
        # Calculate fitness: Find fitness scores for all VMs
        fitness_scores = self._get_fitness_scores(task)
        
        # Find the "Alpha" VM (the one with the minimum fitness score)
        alpha_vm_id = np.argmin(fitness_scores)
        
        chosen_vm_id = -1
        phase = ""
        log_reason = ""
        
        # --- RHO Phases ---
        r1 = random.random() # 0.0 to 1.0
        
        if r1 < 0.5:
            # --- Phase 1: Exploration (Male Rock Hyrax) ---
            
            phase = "Phase 1 (Exploration)"
            r2 = random.random()
            if r2 < 0.5:
                # Eq. 8: Explore a completely random solution
                chosen_vm_id = random.randint(0, self.num_vms - 1)
                log_reason = "Random Search"
            else:
                # Eq. 9: Move towards the best (Alpha)
                chosen_vm_id = alpha_vm_id
                log_reason = "Towards Alpha"
        else:
            # --- Phase 2: Exploitation (Female Rock Hyrax) ---
            phase = "Phase 2 (Exploitation)"
            # Eq. 10 & 11: Exploit the best (Alpha)
            chosen_vm_id = alpha_vm_id
            log_reason = "Best (Alpha)"
            
        # --- Logging ---
        if log_tasks and len(self.log) < 50: # Log first 50 tasks
            log_msg = f"Task {task['id']}: Alpha VM={alpha_vm_id} (Fit: {fitness_scores[alpha_vm_id]:.2f}). {phase} ({log_reason}). -> Assigned to VM {chosen_vm_id}"
            self.log.append(log_msg)
        # --- End Logging ---
        
        # --- Task Metrics ---
        eft = self._get_expected_finish_times(task)[chosen_vm_id]
        self.task_log.append({
            "response_time": eft
        })
        # --- End Task Metrics ---

        # Assign the task to the chosen VM and update its load
        self.vm_loads[chosen_vm_id] += task['length']

    def simulate(self, tasks, log_tasks=False):
        """Runs the RHO simulation for all tasks."""
        self.reset()
        for task in tasks:
            self.assign_task(task, log_tasks)
        return self.get_vm_finish_times()