# --- Default Simulation Parameters ---
DEFAULT_NUM_VMS = 20
DEFAULT_VM_MIPS_RANGE = (100, 1000)
DEFAULT_TASK_LENGTH_RANGE = (1000, 50000)
DEFAULT_TASK_STEPS = [200, 400, 600, 800, 1000]
DEFAULT_RHO_WEIGHTS = (0.7, 0.3) # (w1_time, w2_energy)
DEFAULT_ACO_PARAMS = (1.0, 2.0, 0.1) # (alpha, beta, evap_rate)

def get_default_params():
    """Returns a dictionary of the default parameters."""
    return {
        "NUM_VMS": DEFAULT_NUM_VMS,
        "VM_MIPS_RANGE": DEFAULT_VM_MIPS_RANGE,
        "TASK_LENGTH_RANGE": DEFAULT_TASK_LENGTH_RANGE,
        "TASK_STEPS": DEFAULT_TASK_STEPS,
        "RHO_WEIGHTS": DEFAULT_RHO_WEIGHTS,
        "ACO_PARAMS": DEFAULT_ACO_PARAMS
    }