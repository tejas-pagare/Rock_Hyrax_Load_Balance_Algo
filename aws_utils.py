import boto3
from decimal import Decimal
import json

# Global clients, initialized by main
dynamodb_client = None
dynamodb_resource = None

def init_clients(profile_name=None):
    """Initialize Boto3 clients with an optional profile."""
    global dynamodb_client, dynamodb_resource
    session = boto3.Session(profile_name=profile_name)
    
    dynamodb_client = session.client('dynamodb')
    dynamodb_resource = session.resource('dynamodb')

def clear_dynamodb_table(table_name):
    """
    Scans and deletes all items from a DynamoDB table.
    This fulfills the "delete previous logs" requirement.
    """
    if not dynamodb_resource or not dynamodb_client:
        raise Exception("AWS clients not initialized. Call init_clients() first.")

    table = dynamodb_resource.Table(table_name)
    
    # Get the primary key schema
    try:
        table_desc = dynamodb_client.describe_table(TableName=table_name)
        key_schema = table_desc['Table']['KeySchema']
        keys_to_project = [k['AttributeName'] for k in key_schema]
    except Exception as e:
        print(f"Could not describe table {table_name}. Assuming standard keys (RunID, AlgorithmTaskCount)...")
        keys_to_project = ['RunID', 'AlgorithmTaskCount']

    # Scan for items (projection expression to get only keys)
    scan_kwargs = {
        'ProjectionExpression': ", ".join(keys_to_project)
    }
    
    items_to_delete = []
    response = table.scan(**scan_kwargs)
    items_to_delete.extend(response.get('Items', []))
    
    while 'LastEvaluatedKey' in response:
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        response = table.scan(**scan_kwargs)
        items_to_delete.extend(response.get('Items', []))

    if not items_to_delete:
        print("Table is already empty.")
        return

    # Batch delete items
    with table.batch_writer() as batch:
        for item in items_to_delete:
            batch.delete_item(Key=item)
            
    print(f"Deleted {len(items_to_delete)} items from {table_name}.")


def log_results_to_dynamodb(table_name, run_id, experiment_results, sim_params, final_times=None, assignment_logs=None):
    """
    Logs the experiment results to the specified DynamoDB table.
    
    Schema:
    - PrimaryKey: RunID (str)
    - SortKey: AlgorithmTaskCount (str, e.g., "ACO-400")
    - Other attributes: Algorithm (str), TaskCount (int), and all metrics.
    """
    if not dynamodb_resource:
        raise Exception("AWS clients not initialized. Call init_clients() first.")

    table = dynamodb_resource.Table(table_name)
    
    with table.batch_writer() as batch:
        # Log simulation parameters as a special item
        params_key = f"params"
        params_item = {
            'RunID': run_id,
            'AlgorithmTaskCount': params_key,
            'Algorithm': 'SimulationParameters',
            'Params': json.loads(json.dumps(sim_params), parse_float=Decimal) # Store params
        }
        batch.put_item(Item=params_item)

        # Log experiment results (per task_count and algorithm)
        for task_count, algos in experiment_results.items():
            for algo_name, metrics in algos.items():
                
                # Create the composite sort key
                item_key = f"{algo_name}-{task_count}"
                
                # Convert floats to Decimals for DynamoDB
                metrics_decimal = {k: Decimal(str(v)) for k, v in metrics.items()}
                
                item = {
                    'RunID': run_id,
                    'AlgorithmTaskCount': item_key,
                    'Algorithm': algo_name,
                    'TaskCount': task_count,
                    **metrics_decimal
                }
                
                batch.put_item(Item=item)

        # Optionally store final per-VM finish times for bar charts (max tasks)
        if final_times:
            max_tasks = None
            try:
                # Use configured max task step when present
                max_tasks = sim_params.get('TASK_STEPS', [])[-1]
            except Exception:
                max_tasks = None

            for algo_name, times in final_times.items():
                # Convert numpy arrays to list and floats to Decimals
                try:
                    as_list = [float(x) for x in list(times)]
                except Exception:
                    continue
                item = {
                    'RunID': run_id,
                    'AlgorithmTaskCount': f"FinalTimes-{algo_name}",
                    'Algorithm': algo_name,
                    'TaskCount': max_tasks if max_tasks is not None else 0,
                    'NumVMs': len(as_list),
                    'VmFinishTimes': [Decimal(str(v)) for v in as_list],
                }
                batch.put_item(Item=item)

        # Optionally store assignment logs (first 50 entries per algorithm)
        if assignment_logs:
            for algo_name, logs in assignment_logs.items():
                if not logs:
                    continue
                item = {
                    'RunID': run_id,
                    'AlgorithmTaskCount': f"AssignmentLog-{algo_name}",
                    'Algorithm': algo_name,
                    'Logs': logs[:50],
                }
                batch.put_item(Item=item)
                
# S3 upload functionality removed; DynamoDB logging remains for metrics and final VM times.