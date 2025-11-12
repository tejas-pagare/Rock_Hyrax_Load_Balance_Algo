import argparse
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

# Reuse the existing plotting helpers
import plotting


def _to_float(v):
    """Convert DynamoDB Decimals (and nested structures) to Python floats."""
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, dict):
        return {k: _to_float(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_to_float(x) for x in v]
    return v


def fetch_experiment_results(table, run_id: str):
    """
    Fetch items for a given RunID from DynamoDB and reconstruct the
    experiment_results structure expected by plotting.plot_experiment_graphs:

    {
      task_count(int): {
         "Round Robin"|"RHO"|"ACO": { metric_name: float, ... }
      },
      ...
    }
    """
    # Query all items under the partition key
    resp = table.query(
        KeyConditionExpression=Key("RunID").eq(run_id)
    )

    items = resp.get("Items", [])
    while "LastEvaluatedKey" in resp:
        resp = table.query(
            KeyConditionExpression=Key("RunID").eq(run_id),
            ExclusiveStartKey=resp["LastEvaluatedKey"],
        )
        items.extend(resp.get("Items", []))

    results = {}
    final_times = {}
    max_tasks = None
    for it in items:
        sort_key = it.get("AlgorithmTaskCount")
        algo = it.get("Algorithm")

        # Parameters item
        if algo == "SimulationParameters" or sort_key == "params":
            # Optionally capture max_tasks from params
            try:
                params = it.get("Params")
                if isinstance(params, dict) and "TASK_STEPS" in params and params["TASK_STEPS"]:
                    seq = params["TASK_STEPS"]
                    if isinstance(seq, list) and len(seq) > 0:
                        max_tasks = int(seq[-1])
            except Exception:
                pass
            continue

        # Final per-VM times
        if isinstance(sort_key, str) and sort_key.startswith("FinalTimes-"):
            if algo and "VmFinishTimes" in it:
                final_times[algo] = [_to_float(x) for x in it["VmFinishTimes"]]
            if max_tasks is None and "TaskCount" in it:
                try:
                    max_tasks = int(it["TaskCount"])
                except Exception:
                    pass
            continue

        task_count = int(it.get("TaskCount")) if "TaskCount" in it else None
        if task_count is None or not algo:
            continue

        # Collect metrics: everything that is a number except keys
        metrics = {}
        for k, v in it.items():
            if k in ("RunID", "AlgorithmTaskCount", "Algorithm", "TaskCount"):
                continue
            # Only numeric metrics
            if isinstance(v, (int, float, Decimal)):
                metrics[k] = _to_float(v)

        if not metrics:
            continue

        results.setdefault(task_count, {})[algo] = metrics

    return results, final_times, max_tasks


def main():
    parser = argparse.ArgumentParser(description="Generate plots from DynamoDB logs for a given RunID")
    parser.add_argument("--run-id", required=True, help="RunID to visualize (e.g., sim-run-YYYY-MM-DD-HHMMSS-xxxxxx)")
    parser.add_argument("--dynamo-table", default="LoadBalancingSimResults", help="DynamoDB table name")
    parser.add_argument("--aws-profile", default=None, help="AWS CLI profile to use")
    args = parser.parse_args()

    # Init session
    session = boto3.Session(profile_name=args.aws_profile) if args.aws_profile else boto3.Session()
    ddb = session.resource("dynamodb")
    table = ddb.Table(args.dynamo_table)

    print(f"Fetching results from DynamoDB table '{args.dynamo_table}' for RunID '{args.run_id}' ...")
    experiment_results, final_times, max_tasks = fetch_experiment_results(table, args.run_id)
    if not experiment_results:
        print("No results found. Double-check RunID and table.")
        return

    # 1) Line chart across task counts
    out_line = plotting.plot_experiment_graphs(experiment_results)
    if out_line:
        print(f"Generated plot: {out_line}")
    else:
        print("Line plot generation returned no output (possibly missing data).")

    # 2) Bar charts for the final run (requires FinalTimes items)
    try:
        max_tc = max_tasks if max_tasks is not None else max(experiment_results.keys())
    except Exception:
        max_tc = None

    if final_times and max_tc is not None:
        final_metrics = experiment_results.get(max_tc, {})
        # Determine num_vms from any algorithm's list
        any_algo = next(iter(final_times))
        num_vms = len(final_times[any_algo])
        out_files = plotting.plot_single_run_results(final_times, final_metrics, num_vms)
        for f in out_files:
            print(f"Generated plot: {f}")
    else:
        print("No FinalTimes found in DynamoDB; bar charts cannot be generated from logs.")


if __name__ == "__main__":
    main()
