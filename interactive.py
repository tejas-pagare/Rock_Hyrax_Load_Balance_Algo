import config

def get_simulation_parameters():
    """
    Interactively prompts the user to set simulation parameters.
    Returns a dictionary of the chosen parameters.
    """
    
    params = config.get_default_params()

    print("=" * 40)
    print("--- Load Balancing Simulation Setup ---")
    print("=" * 40)
    print(f"Default Parameters:")
    print(f"  1. Number of VMs:         {params['NUM_VMS']}")
    print(f"  2. VM MIPS Range (min, max): {params['VM_MIPS_RANGE']}")
    print(f"  3. Task Length Range (min, max): {params['TASK_LENGTH_RANGE']}")
    print(f"  4. Task Steps (e.g., 200, 400,...): {params['TASK_STEPS']}")
    print(f"  5. RHO Weights (w1_time, w2_energy): {params['RHO_WEIGHTS']}")
    print(f"  6. ACO Params (alpha, beta, evap_rate): {params['ACO_PARAMS']}")
    print("-" * 40)

    use_defaults = input("Run simulation with default parameters? (yes/no): ").strip().lower()

    if use_defaults in ['n', 'no']:
        # --- Get Custom User Inputs ---
        print("--- Enter Custom Simulation Parameters ---")
        try:
            params["NUM_VMS"] = int(input(f"  1. Number of VMs (default: {params['NUM_VMS']}): ") or params['NUM_VMS'])
            
            vm_min_mips = int(input(f"  2a. VM Min MIPS (default: {params['VM_MIPS_RANGE'][0]}): ") or params['VM_MIPS_RANGE'][0])
            vm_max_mips = int(input(f"  2b. VM Max MIPS (default: {params['VM_MIPS_RANGE'][1]}): ") or params['VM_MIPS_RANGE'][1])
            params["VM_MIPS_RANGE"] = (vm_min_mips, vm_max_mips)
            
            task_min_len = int(input(f"  3a. Task Min Length (MI) (default: {params['TASK_LENGTH_RANGE'][0]}): ") or params['TASK_LENGTH_RANGE'][0])
            task_max_len = int(input(f"  3b. Task Max Length (MI) (default: {params['TASK_LENGTH_RANGE'][1]}): ") or params['TASK_LENGTH_RANGE'][1])
            params["TASK_LENGTH_RANGE"] = (task_min_len, task_max_len)

            task_steps_str = input(f"  4. Task Steps (comma-sep list) (default: {params['TASK_STEPS']}): ") or str(params['TASK_STEPS'])
            params["TASK_STEPS"] = [int(s.strip()) for s in task_steps_str.replace('[','').replace(']','').split(',')]
            
            w1 = float(input(f"  5a. RHO Weight w1 (Time) (default: {params['RHO_WEIGHTS'][0]}): ") or params['RHO_WEIGHTS'][0])
            w2 = float(input(f"  5b. RHO Weight w2 (Energy) (default: {params['RHO_WEIGHTS'][1]}): ") or params['RHO_WEIGHTS'][1])
            params["RHO_WEIGHTS"] = (w1, w2)
            
            if w1 + w2 != 1.0:
                print(f"Warning: RHO Weights w1 ({w1}) and w2 ({w2}) do not add up to 1.0. Normalizing...")
                total = w1 + w2
                w1 = w1 / total
                w2 = w2 / total
                params["RHO_WEIGHTS"] = (w1, w2)
                print(f"Normalized Weights: w1_time={w1:.2f}, w2_energy={w2:.2f}")

            alpha = float(input(f"  6a. ACO Alpha (pheromone) (default: {params['ACO_PARAMS'][0]}): ") or params['ACO_PARAMS'][0])
            beta = float(input(f"  6b. ACO Beta (heuristic) (default: {params['ACO_PARAMS'][1]}): ") or params['ACO_PARAMS'][1])
            evap = float(input(f"  6c. ACO Evap. Rate (0.0-1.0) (default: {params['ACO_PARAMS'][2]}): ") or params['ACO_PARAMS'][2])
            params["ACO_PARAMS"] = (alpha, beta, evap)

        except ValueError:
            print("Invalid input. Reverting to default parameters.")
            params = config.get_default_params()
    else:
        print("Using default parameters.")
    
    return params