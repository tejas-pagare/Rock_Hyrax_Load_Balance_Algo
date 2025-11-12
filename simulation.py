import random
import numpy as np
import simpy

from entities import create_vm, create_task
from algorithms.round_robin import RoundRobinBalancer
from algorithms.rho import RockHyraxBalancer
from algorithms.aco import AntColonyBalancer
import metrics


def _simulate_with_simpy(balancer, tasks, vms, log_tasks=False):
    """
    Run a discrete-event simulation for a single balancer using SimPy.
    Semantics: all tasks arrive at t=0 in the given order; each VM is a single-server queue (FCFS).
    Balancer decides the VM per task; we then process tasks on that VM at service_time = length/mips.
    Returns an array of per-VM finish times (i.e., time of last task completion on that VM).
    """
    # Reset balancer internal state for a fresh run
    balancer.reset()

    env = simpy.Environment()

    # One resource per VM (capacity=1) and a completion tracker
    vm_resources = [simpy.Resource(env, capacity=1) for _ in vms]
    vm_last_finish = np.zeros(len(vms), dtype=float)

    def vm_process_task(env, vm_idx, task, resource):
        # Request the VM (FCFS)
        with resource.request() as req:
            yield req
            # Service time in seconds = MI / MIPS
            mips = vms[vm_idx]["mips"]
            service_time = (task['length'] / mips) if mips > 0 else 0
            yield env.timeout(service_time)
            vm_last_finish[vm_idx] = env.now

    # Assign tasks and create processes (arrival time = 0)
    for task in tasks:
        chosen_vm_id = balancer.assign_task(task, log_tasks)
        # Start processing immediately; FCFS order preserved by creation order
        env.process(vm_process_task(env, chosen_vm_id, task, vm_resources[chosen_vm_id]))

    # Run until all tasks finish
    env.run()
    return vm_last_finish

def run_experiment(params):
    """
    Runs the full simulation experiment over a series of task steps.
    """
    
    # --- Setup ---
    print("\n" + "=" * 40)
    print("--- RUNNING EXPERIMENT ---")
    print(f"Testing with task counts: {params['TASK_STEPS']}")
    print(f"VMs: {params['NUM_VMS']}, RHO Weights (T/E): {params['RHO_WEIGHTS'][0]}/{params['RHO_WEIGHTS'][1]}")
    print(f"ACO Params (a/b/e/q0): {params['ACO_PARAMS']}")
    print("=" * 40)

    # Create all VMs. They are shared across all balancers.
    vms = [
        create_vm(i, random.randint(params['VM_MIPS_RANGE'][0], params['VM_MIPS_RANGE'][1]))
        for i in range(params['NUM_VMS'])
    ]
    
    print("--- VM Configuration ---")
    for vm in vms:
        print(f"  VM {vm['id']}: {vm['mips']} MIPS, P_max={vm['p_max']:.0f}W, P_idle={vm['p_idle']:.0f}W")
    
    # Create all balancers
    rr_balancer = RoundRobinBalancer(vms)
    rho_balancer = RockHyraxBalancer(vms, w1=params['RHO_WEIGHTS'][0], w2=params['RHO_WEIGHTS'][1])
    aco_balancer = AntColonyBalancer(vms, *params['ACO_PARAMS'])
    
    balancers = {
        "Round Robin": rr_balancer,
        "RHO": rho_balancer,
        "ACO": aco_balancer
    }

    # Create a master list of tasks
    max_tasks = params['TASK_STEPS'][-1]
    all_tasks = [
        create_task(i, random.randint(params['TASK_LENGTH_RANGE'][0], params['TASK_LENGTH_RANGE'][1]))
        for i in range(max_tasks)
    ]
    
    experiment_results = {}

    # --- Run simulation for each task step ---
    for task_count in params['TASK_STEPS']:
        print(f"...Simulating for {task_count} tasks...")
        
        tasks_subset = all_tasks[:task_count]
        
        # Run simulations (SimPy-based)
        rr_finish_times = _simulate_with_simpy(rr_balancer, tasks_subset, vms, log_tasks=False)
        rho_finish_times = _simulate_with_simpy(rho_balancer, tasks_subset, vms, log_tasks=False)
        aco_finish_times = _simulate_with_simpy(aco_balancer, tasks_subset, vms, log_tasks=False)
        
        # Calculate metrics
        metrics_rr = metrics.calculate_metrics(rr_balancer, rr_finish_times, task_count)
        metrics_rho = metrics.calculate_metrics(rho_balancer, rho_finish_times, task_count)
        metrics_aco = metrics.calculate_metrics(aco_balancer, aco_finish_times, task_count)
        
        # Store results
        experiment_results[task_count] = {
            "Round Robin": metrics_rr,
            "RHO": metrics_rho,
            "ACO": metrics_aco
        }
    
    print("--- EXPERIMENT COMPLETE ---")
    
    # --- Process Final Run (Max Tasks) ---
    print(f"\nProcessing results for max tasks ({params['TASK_STEPS'][-1]})...")
    
    # We re-run the final simulation with logging enabled
    tasks_final = all_tasks[:params['TASK_STEPS'][-1]]
    
    final_times = {
        "Round Robin": _simulate_with_simpy(rr_balancer, tasks_final, vms, log_tasks=True),
        "RHO": _simulate_with_simpy(rho_balancer, tasks_final, vms, log_tasks=True),
        "ACO": _simulate_with_simpy(aco_balancer, tasks_final, vms, log_tasks=True)
    }
    
    final_metrics = {
        "Round Robin": metrics.calculate_metrics(rr_balancer, final_times["Round Robin"], params['TASK_STEPS'][-1]),
        "RHO": metrics.calculate_metrics(rho_balancer, final_times["RHO"], params['TASK_STEPS'][-1]),
        "ACO": metrics.calculate_metrics(aco_balancer, final_times["ACO"], params['TASK_STEPS'][-1])
    }
    
    return experiment_results, final_metrics, final_times, balancers