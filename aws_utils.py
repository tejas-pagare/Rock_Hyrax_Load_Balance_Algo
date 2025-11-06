import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import json

# Global clients, initialized by main
dynamodb_client = None
dynamodb_resource = None
s3_client = None

def init_clients(profile_name=None):
    """Initialize Boto3 clients with an optional profile."""
    global dynamodb_client, dynamodb_resource, s3_client
    session = boto3.Session(profile_name=profile_name)
    
    dynamodb_client = session.client('dynamodb')
    dynamodb_resource = session.resource('dynamodb')
    s3_client = session.client('s3')

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


def log_results_to_dynamodb(table_name, run_id, experiment_results, sim_params):
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

        # Log experiment results
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
                
def upload_graphs_to_s3(bucket_name, run_id, plot_files):
    """
    Uploads the generated .png graph files to an S3 bucket
    under a folder named after the run_id.
    """
    if not s3_client:
        raise Exception("AWS clients not initialized. Call init_clients() first.")
        
    for file_name in plot_files:
        try:
            s3_key = f"{run_id}/{file_name}" # e.g., sim-run-123/performance_graphs.png
            s3_client.upload_file(
                file_name,
                bucket_name,
                s3_key,
                ExtraArgs={'ContentType': 'image/png'}
            )
            print(f"Successfully uploaded {file_name} to s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print(f"Error uploading {file_name} to S3: {e}")