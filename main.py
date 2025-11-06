import argparse
import uuid
import time
from datetime import datetime

import config
import interactive
import simulation
import aws_utils

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
        help="Name of the S3 bucket to upload graphs to"
    )
    parser.add_argument(
        '--skip-interactive',
        action='store_true',
        help="Skip interactive prompts and use default parameters"
    )
    
    args = parser.parse_args()
    
    # --- AWS Validation ---
    if args.aws_enabled:
        if not args.s3_bucket:
            print("Error: --s3-bucket is required when --aws-enabled is set.")
            print("Please provide an S3 bucket to upload graph artifacts.")
            exit(1)
        print(f"--- AWS Mode Enabled ---")
        print(f"Profile: {args.aws_profile or 'default'}")
        print(f"DynamoDB Table: {args.dynamo_table}")
        print(f"S3 Bucket: {args.s3_bucket}")
        print("--------------------------")
        
        # Initialize AWS clients
        aws_utils.init_clients(args.aws_profile)

    # --- Get Simulation Parameters ---
    if args.skip_interactive:
        print("Skipping interactive setup, using default parameters.")
        sim_params = config.get_default_params()
    else:
        sim_params = interactive.get_simulation_parameters()
    
    # Generate a unique ID for this simulation run
    run_id = f"sim-run-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    print(f"\nStarting simulation with RunID: {run_id}")

    # --- AWS: Clear Previous Results ---
    if args.aws_enabled:
        print(f"Clearing previous results from DynamoDB table: {args.dynamo_table}...")
        try:
            aws_utils.clear_dynamodb_table(args.dynamo_table)
            print("DynamoDB table cleared.")
        except Exception as e:
            print(f"Error clearing DynamoDB table: {e}")
            print("Continuing simulation without clearing. Table may not exist or permissions may be missing.")
            
    # --- Run Simulation ---
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

    # 4. Log to AWS (if enabled)
    if args.aws_enabled:
        print("\n--- Logging results to AWS ---")
        try:
            # Log experiment data to DynamoDB
            print("Logging experiment data to DynamoDB...")
            aws_utils.log_results_to_dynamodb(
                args.dynamo_table, 
                run_id, 
                experiment_results,
                sim_params
            )
            print("DynamoDB logging complete.")

            # Upload graph files to S3
            print("Uploading graph files to S3...")
            aws_utils.upload_graphs_to_s3(
                args.s3_bucket,
                run_id,
                plot_files
            )
            print("S3 upload complete.")
            print(f"\nFind your results in S3 bucket '{args.s3_bucket}' under prefix (folder) '{run_id}/'")

        except Exception as e:
            print(f"--- AWS Logging Failed ---")
            print(f"Error: {e}")
            print("Please check your AWS credentials, IAM permissions, and resource names.")

    print("\nSimulation finished.")

if __name__ == "__main__":
    main()