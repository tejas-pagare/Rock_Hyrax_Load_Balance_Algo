def create_vm(vm_id, mips):
    """Creates a VM dict with a power model based on MIPS."""
    # Simple model: power scales with MIPS.
    # Paper uses values like 250W. We'll scale around that.
    p_max = (mips * 0.2) + 150  # e.g., 100 MIPS -> 170W, 1000 MIPS -> 350W
    p_idle = p_max * 0.7       # Paper states idle is 70% of max
    return {
        "id": vm_id,
        "mips": mips,
        "p_max": p_max,
        "p_idle": p_idle
    }

def create_task(task_id, length):
    """A Task is defined by its ID and its length in MI (Million Instructions)"""
    return {
        "id": task_id,
        "length": length
    }