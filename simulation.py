import random
import numpy as np

from entities import create_vm, create_task
from algorithms.round_robin import RoundRobinBalancer
from algorithms.rho import RockHyraxBalancer
from algorithms.aco import AntColonyBalancer
import metrics

def run_experiment(params):
    """
    Runs the full simulation experiment over a series of task steps.
    """
    
    # --- Setup ---
    print("\n" + "=" * 40)
    print("--- RUNNING EXPERIMENT ---")
    print(f"Testing with task counts: {params['TASK_STEPS']}")
    print(f"VMs: {params['NUM_VMS']}, RHO Weights (T/E): {params['RHO_WEIGHTS'][0]}/{params['RHO_WEIGHTS'][1]}")
    print(f"ACO Params (a/b/e): {params['ACO_PARAMS']}")
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
        
        # Run simulations
        rr_finish_times = rr_balancer.simulate(tasks_subset)
        rho_finish_times = rho_balancer.simulate(tasks_subset)
        aco_finish_times = aco_balancer.simulate(tasks_subset)
        
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
        "Round Robin": rr_balancer.simulate(tasks_final, log_tasks=True),
        "RHO": rho_balancer.simulate(tasks_final, log_tasks=True),
        "ACO": aco_balancer.simulate(tasks_final, log_tasks=True)
    }
    
    final_metrics = {
        "Round Robin": metrics.calculate_metrics(rr_balancer, final_times["Round Robin"], params['TASK_STEPS'][-1]),
        "RHO": metrics.calculate_metrics(rho_balancer, final_times["RHO"], params['TASK_STEPS'][-1]),
        "ACO": metrics.calculate_metrics(aco_balancer, final_times["ACO"], params['TASK_STEPS'][-1])
    }
    
    return experiment_results, final_metrics, final_times, balancers