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

        # 1) Time cost: expected finish time if assigning this task now (s)
        raw_time_costs = self._get_expected_finish_times(task)

        # 2) Energy cost: incremental energy to execute THIS task on VM i
        #    E_task(i) ≈ P_max(i) * service_time(i), service_time = length / mips
        raw_energy_costs = np.zeros(self.num_vms)
        for i in range(self.num_vms):
            vm = self.vms[i]
            mips = vm.get("mips", 0)
            if mips > 0:
                service_time = task['length'] / mips
                raw_energy_costs[i] = vm["p_max"] * service_time
            else:
                raw_energy_costs[i] = float('inf')

        # 3) Normalize costs (min-max) into [0,1]
        min_time, max_time = np.min(raw_time_costs), np.max(raw_time_costs)
        min_energy, max_energy = np.min(raw_energy_costs), np.max(raw_energy_costs)

        norm_time = (raw_time_costs - min_time) / (max_time - min_time + 1e-9)
        norm_energy = (raw_energy_costs - min_energy) / (max_energy - min_energy + 1e-9)

        # 4) Weighted fitness (lower is better)
        fitness_scores = (self.w1 * norm_time) + (self.w2 * norm_energy)
        return fitness_scores

    def assign_task(self, task, log_tasks=False):
        """
        Assigns a single task using the RHO logic (Phases 1 and 2).
        """
        # Calculate fitness for all VMs
        fitness_scores = self._get_fitness_scores(task)

        # Identify Alpha (best current VM)
        alpha_vm_id = int(np.argmin(fitness_scores))

        # Exploration vs Exploitation via temperature-controlled softmax
        r = random.random()
        if r < 0.5:
            phase = "Phase 1 (Exploration)"
            temperature = 1.0  # high temp => more uniform probabilities
        else:
            phase = "Phase 2 (Exploitation)"
            temperature = 0.2  # low temp => focus on best (alpha)

        # Stable softmax over negative fitness (lower fitness => higher prob)
        scores = -fitness_scores / max(temperature, 1e-9)
        scores -= np.max(scores)  # numerical stability
        exps = np.exp(scores)
        probs = exps / (np.sum(exps) + 1e-12)

        # Draw VM; ensure at least some chance for alpha in exploration, too
        chosen_vm_id = int(np.random.choice(self.num_vms, p=probs))
        log_reason = f"Softmax sample (T={temperature:.2f})"

        # Logging (first 50 tasks)
        if log_tasks and len(self.log) < 50:
            log_msg = (
                f"Task {task['id']}: Alpha VM={alpha_vm_id} (Fit: {fitness_scores[alpha_vm_id]:.3f}). "
                f"{phase} ({log_reason}). -> Assigned to VM {chosen_vm_id} (p={probs[chosen_vm_id]:.3f})"
            )
            self.log.append(log_msg)

        # Task metrics based on expected finish time at decision time
        eft = self._get_expected_finish_times(task)[chosen_vm_id]
        self.task_log.append({"response_time": eft})

        # Update VM load (sum of MI assigned)
        self.vm_loads[chosen_vm_id] += task['length']

        # Return chosen VM id for SimPy integration
        return chosen_vm_id

    def simulate(self, tasks, log_tasks=False):
        """Runs the RHO simulation for all tasks."""
        self.reset()
        for task in tasks:
            self.assign_task(task, log_tasks)
        return self.get_vm_finish_times()