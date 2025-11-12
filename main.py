import argparse
import uuid
import time
from datetime import datetime

import config
import interactive
import simulation
import aws_utils
import metrics
import plotting

def run_simulation(sim_params):
    """Runs the simulation and returns the results."""
    start_time = time.time()
    
    experiment_results, final_metrics, final_times, balancers = simulation.run_experiment(sim_params)
    
    end_time = time.time()
    print(f"\n--- EXPERIMENT COMPLETE ({end_time - start_time:.2f} seconds) ---")

    # --- Process and Log Results ---
    
    # 1. Print console comparison
    metrics.print_comparison(final_metrics)
    
    # 2. Generate local graph files
    plot_files = plotting.generate_all_plots(
        final_times, 
        final_metrics, 
        sim_params['NUM_VMS'], 
        experiment_results
    )
    print("\nGenerated local graph files:")
    for file in plot_files:
        print(f"- {file}")

    # 3. Print assignment logs
    metrics.print_assignment_logs(balancers)
    
    return experiment_results, plot_files, final_metrics, final_times, balancers


def handle_aws_operations(args, run_id, sim_params, experiment_results, plot_files, final_metrics=None, final_times=None, balancers=None):
    """Handles all AWS-related operations."""
    if not args.aws_enabled:
        return

    print("\n--- Logging results to AWS ---")
    try:
        # Clear previous results from DynamoDB
        print(f"Clearing previous results from DynamoDB table: {args.dynamo_table}...")
        aws_utils.clear_dynamodb_table(args.dynamo_table)
        print("DynamoDB table cleared.")

        # Log experiment data to DynamoDB
        print("Logging experiment data to DynamoDB...")
        aws_utils.log_results_to_dynamodb(
            args.dynamo_table,
            run_id,
            experiment_results,
            sim_params,
            final_times=final_times,
            assignment_logs={
                name: (balancer.log if hasattr(balancer, 'log') else [])
                for name, balancer in (balancers or {}).items()
            } if balancers else None,
        )
        print("DynamoDB logging complete.")

        # Note: S3 uploads removed. Graphs are stored locally; DynamoDB holds metrics and final VM times.

    except Exception as e:
        print(f"--- AWS Logging Failed ---")
        print(f"Error: {e}")
        print("Please check your AWS credentials, IAM permissions, and resource names.")


def main():
    """
    Main entry point for the load balancing simulation.
    
    Parses arguments, gets configuration, runs the simulation,
    and logs results locally and to AWS if specified.
    """
    
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Cloud Load Balancing Simulation (RR, RHO, ACO)")
    parser.add_argument(
        '--aws-enabled', 
        action='store_true', 
        help="Enable logging results to AWS (DynamoDB and S3)"
    )
    parser.add_argument(
        '--aws-profile', 
        default=None, 
        help="AWS profile name to use (if not default)"
    )
    parser.add_argument(
        '--dynamo-table', 
        default='LoadBalancingSimResults', 
        help="Name of the DynamoDB table to use"
    )
    parser.add_argument(
        '--s3-bucket',
        default=None,
        help=argparse.SUPPRESS  # Deprecated; S3 uploads removed
    )
    parser.add_argument(
        '--skip-interactive',
        action='store_true',
        help="Skip interactive prompts and use default parameters"
    )
    # Simulation parameter overrides via CLI
    parser.add_argument('--num-vms', type=int, default=None, help='Number of VMs')
    parser.add_argument('--vm-mips-range', type=str, default=None, help='VM MIPS range as min,max')
    parser.add_argument('--task-length-range', type=str, default=None, help='Task length range (MI) as min,max')
    parser.add_argument('--task-steps', type=str, default=None, help='Comma-separated task counts, e.g., 200,400,600')
    parser.add_argument('--rho-weights', type=str, default=None, help='RHO weights as w1,w2')
    parser.add_argument('--aco-params', type=str, default=None, help='ACO params as alpha,beta,evap[,q0]')
    parser.add_argument('--random-seed', type=int, default=None, help='Random seed for reproducible runs')
    
    args = parser.parse_args()
    
    # --- AWS Validation ---
    if args.aws_enabled:
        print(f"--- AWS Mode Enabled ---")
        print(f"Profile: {args.aws_profile or 'default'}")
        print(f"DynamoDB Table: {args.dynamo_table}")
        print("--------------------------")
        
        # Initialize AWS clients
        aws_utils.init_clients(args.aws_profile)

    # --- Get Simulation Parameters ---
    def parse_pair(s):
        a, b = [x.strip() for x in s.split(',')]
        return int(a), int(b)

    def parse_list_ints(s):
        return [int(x.strip()) for x in s.split(',') if x.strip()]

    def parse_floats(s):
        return [float(x.strip()) for x in s.split(',') if x.strip()]

    # Gather defaults first
    sim_params = config.get_default_params()

    # Apply CLI overrides if provided
    overrides_used = False
    if args.num_vms is not None:
        sim_params['NUM_VMS'] = args.num_vms; overrides_used = True
    if args.vm_mips_range:
        sim_params['VM_MIPS_RANGE'] = parse_pair(args.vm_mips_range); overrides_used = True
    if args.task_length_range:
        sim_params['TASK_LENGTH_RANGE'] = parse_pair(args.task_length_range); overrides_used = True
    if args.task_steps:
        sim_params['TASK_STEPS'] = parse_list_ints(args.task_steps); overrides_used = True
    if args.rho_weights:
        w = parse_floats(args.rho_weights)
        if len(w) != 2:
            raise ValueError('--rho-weights must be w1,w2')
        total = w[0] + w[1]
        if total <= 0:
            raise ValueError('RHO weights must be positive')
        sim_params['RHO_WEIGHTS'] = (w[0]/total, w[1]/total)
        overrides_used = True
    if args.aco_params:
        ap = parse_floats(args.aco_params)
        if len(ap) not in (3,4):
            raise ValueError('--aco-params must be alpha,beta,evap[,q0]')
        if len(ap) == 3:
            ap.append(0.0)
        sim_params['ACO_PARAMS'] = tuple(ap[:4])
        overrides_used = True

    if not overrides_used and not args.skip_interactive:
        sim_params = interactive.get_simulation_parameters()
    else:
        if overrides_used:
            print('Using CLI overrides for simulation parameters.')
        else:
            print('Skipping interactive setup, using default parameters.')
    
    # Generate a unique ID for this simulation run
    run_id = f"sim-run-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    print(f"\nStarting simulation with RunID: {run_id}")

    # --- Run Simulation ---
    if args.random_seed is not None:
        import random as _r
        import numpy as _np
        _r.seed(args.random_seed)
        _np.random.seed(args.random_seed)
        print(f"Random seed set to {args.random_seed}")

    experiment_results, plot_files, final_metrics, final_times, balancers = run_simulation(sim_params)

    # --- Handle AWS Operations ---
    handle_aws_operations(args, run_id, sim_params, experiment_results, plot_files, final_metrics, final_times, balancers)

    print("\nSimulation finished.")

if __name__ == "__main__":
    main()