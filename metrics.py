import numpy as np

def calculate_metrics(balancer, vm_finish_times, num_tasks):
    """
    Calculates and returns key performance metrics from the simulation results.
    """
    
    # 1. Makespan (Eq. 1)
    makespan = np.max(vm_finish_times)
    
    # 2. Average Response Time (Eq. 2)
    # (Sum of all task response times) / (Num tasks)
    all_rts = [log['response_time'] for log in balancer.task_log]
    avg_response_time = np.mean(all_rts) if all_rts else 0
    
    # 3. Throughput
    # (Num tasks) / (Total time)
    throughput = num_tasks / makespan if makespan > 0 else 0
    
    # 4. Total Energy Consumption (Eq. 3 & 4)
    total_energy = 0
    for i in range(balancer.num_vms):
        vm = balancer.vms[i]
        busy_time = vm_finish_times[i]
        
        # Idle time is the duration from when the VM finishes its
        # work until the entire simulation (makespan) ends.
        idle_time = makespan - busy_time
        if idle_time < 0: idle_time = 0 # Handle potential float precision
        
        energy_busy = vm["p_max"] * busy_time
        energy_idle = vm["p_idle"] * idle_time
        
        total_energy += (energy_busy + energy_idle)
        
    return {
        "Makespan_s": makespan,
        "AvgResponseTime_s": avg_response_time,
        "Throughput_task_s": throughput,
        "TotalEnergy_kJ": total_energy / 1000 # Convert W-s to kJ
    }

def print_comparison(metrics_dict):
    """Prints a formatted comparison of the algorithms."""
    print("\n" + "=" * 130)
    print("--- ALGORITHM COMPARISON RESULTS (FOR MAX TASKS) ---")
    print("=" * 130)
    
    algorithms = list(metrics_dict.keys())
    baseline_key = "Round Robin" # Assume RR is the baseline
    
    if baseline_key not in metrics_dict:
        print("Error: Baseline 'Round Robin' not in metrics.")
        return
        
    baseline_metrics = metrics_dict[baseline_key]

    headers = ["Metric"] + algorithms + ["Improvement (RHO vs RR)", "Improvement (ACO vs RR)"]
    
    print(f"{headers[0]:<22} | " +
          f"{headers[1]:<15} | " +
          f"{headers[2]:<15} | " +
          f"{headers[3]:<15} | " +
          f"{headers[4]:<25} | " +
          f"{headers[5]:<25}")
    print("-" * 130)

    for key in baseline_metrics.keys():
        rr_val = baseline_metrics[key]
        rho_val = metrics_dict["RHO"][key]
        aco_val = metrics_dict["ACO"][key]
        
        row = [f"{key:<22}", f"{rr_val:<15.2f}", f"{rho_val:<15.2f}", f"{aco_val:<15.2f}"]

        # Calculate improvements vs Round Robin
        def calc_imp(val, base):
            if "Throughput" not in key: # Lower is better
                return ((base - val) / base) * 100 if base > 0 else 0
            else: # Higher is better
                return ((val - base) / base) * 100 if base > 0 else 0
        
        imp_rho = calc_imp(rho_val, rr_val)
        imp_aco = calc_imp(aco_val, rr_val)
        
        row.append(f"{imp_rho:>25.2f}%")
        row.append(f"{imp_aco:>25.2f}%")
        
        print(" | ".join(row))
        
    print("=" * 130)
    print("* Improvement shows performance vs. Round Robin.")

def print_assignment_logs(balancers):
    """Prints the first 50 assignment logs for each balancer."""
    print("\n" + "-" * 40)
    print("--- Assignment Logs (First 50 Tasks of Final Run) ---")
    print("-" * 40)
    
    for algo_name, balancer in balancers.items():
        print(f"\n--- {algo_name} Assignment Log ---")
        for log_entry in balancer.log:
            print(log_entry)
        if not balancer.log:
            print("No log entries.")
    print("-" * 40)