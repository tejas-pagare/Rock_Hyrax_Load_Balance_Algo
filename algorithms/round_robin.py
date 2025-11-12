from .base import LoadBalancer

class RoundRobinBalancer(LoadBalancer):
    """
    Implements the Round Robin load balancing algorithm.
    It assigns tasks to VMs in a simple cyclic order.
    """
    def __init__(self, vms):
        super().__init__(vms)
        self.rr_counter = 0 # Round Robin counter
    
    def assign_task(self, task, log_tasks=False):
        """Assigns a task using Round Robin logic."""
        # Get the next VM in the cycle
        chosen_vm_id = self.rr_counter % self.num_vms
        
        # --- Logging ---
        if log_tasks and len(self.log) < 50: # Log first 50 tasks
            log_msg = f"Task {task['id']}: Assigned to VM {chosen_vm_id} (Round Robin cycle)"
            self.log.append(log_msg)
        # --- End Logging ---
        
        # --- Task Metrics ---
        eft = self._get_expected_finish_times(task)[chosen_vm_id]
        
        self.task_log.append({
            "response_time": eft # Since AT=0, RT = FT
        })
        # --- End Task Metrics ---

        # Assign the task and update the load
        self.vm_loads[chosen_vm_id] += task['length']
        
        # Increment the counter for the next task
        self.rr_counter += 1
        
        # Return selected VM id for external simulators (e.g., SimPy)
        return chosen_vm_id
        
    def simulate(self, tasks, log_tasks=False):
        """Runs the Round Robin simulation for all tasks."""
        self.reset()
        for task in tasks:
            self.assign_task(task, log_tasks)
        return self.get_vm_finish_times()