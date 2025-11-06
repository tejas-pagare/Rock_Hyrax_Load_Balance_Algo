import numpy as np

class LoadBalancer:
    """
    Base class for load balancing algorithms.
    """
    def __init__(self, vms):
        self.vms = vms
        self.num_vms = len(vms)
        # vm_loads stores the total MI assigned to each VM
        self.vm_loads = np.zeros(self.num_vms)
        self.log = [] # Add log to store assignment decisions
        self.task_log = [] # Stores detailed task metrics
    
    def get_vm_finish_times(self):
        """Calculates the finish time for each VM."""
        finish_times = np.zeros(self.num_vms)
        for i in range(self.num_vms):
            if self.vms[i]["mips"] > 0:
                finish_times[i] = self.vm_loads[i] / self.vms[i]["mips"]
        return finish_times

    def _get_expected_finish_times(self, task):
        """Calculates the raw expected finish time for a task on all VMs."""
        efts = np.zeros(self.num_vms)
        for i in range(self.num_vms):
            vm = self.vms[i]
            if vm["mips"] > 0:
                efts[i] = (self.vm_loads[i] + task['length']) / vm["mips"]
            else:
                efts[i] = float('inf')
        return efts

    def reset(self):
        """Resets the VM loads for a new simulation."""
        self.vm_loads = np.zeros(self.num_vms)
        self.log = [] # Reset log
        self.task_log = [] # Reset task log