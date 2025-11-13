import boto3
from typing import Dict, Any, Optional


def _get_session(profile_name: Optional[str] = None) -> boto3.session.Session:
    return boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()


def _normalize(values: Dict[str, float], higher_is_better: bool) -> Dict[str, float]:
    if not values:
        return {}
    v_list = list(values.values())
    v_min = min(v_list)
    v_max = max(v_list)
    if v_max == v_min:
        # If all equal, give full credit
        return {k: 1.0 for k in values}
    norm: Dict[str, float] = {}
    for k, v in values.items():
        if higher_is_better:
            norm[k] = (v - v_min) / (v_max - v_min)
        else:
            norm[k] = (v_max - v) / (v_max - v_min)
    return norm


def _compute_performance_scores(final_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Compute an overall PerformanceScore in [0,100] combining:
    - AvgResponseTime_s (lower is better) weight 0.5
    - Throughput_task_s (higher is better) weight 0.3
    - TotalEnergy_kJ (lower is better) weight 0.2
    If a metric is missing, its weight is ignored and remaining weights are renormalized.
    """
    # Collect metric maps per algorithm
    resp = {}
    thr = {}
    energy = {}
    for algo, mets in final_metrics.items():
        if 'AvgResponseTime_s' in mets:
            resp[algo] = float(mets['AvgResponseTime_s'])
        if 'Throughput_task_s' in mets:
            thr[algo] = float(mets['Throughput_task_s'])
        if 'TotalEnergy_kJ' in mets:
            energy[algo] = float(mets['TotalEnergy_kJ'])

    # Base weights
    w_resp, w_thr, w_energy = 0.5, 0.3, 0.2
    active_weights = []
    if resp:
        active_weights.append(w_resp)
    else:
        w_resp = 0.0
    if thr:
        active_weights.append(w_thr)
    else:
        w_thr = 0.0
    if energy:
        active_weights.append(w_energy)
    else:
        w_energy = 0.0
    denom = sum(active_weights) or 1.0
    # Renormalize
    w_resp /= denom
    w_thr /= denom
    w_energy /= denom

    resp_n = _normalize(resp, higher_is_better=False) if resp else {}
    thr_n = _normalize(thr, higher_is_better=True) if thr else {}
    energy_n = _normalize(energy, higher_is_better=False) if energy else {}

    algos = set(final_metrics.keys())
    scores: Dict[str, float] = {}
    for a in algos:
        s = 0.0
        if resp_n:
            s += w_resp * resp_n.get(a, 0.0)
        if thr_n:
            s += w_thr * thr_n.get(a, 0.0)
        if energy_n:
            s += w_energy * energy_n.get(a, 0.0)
        scores[a] = 100.0 * s
    return scores


def publish_metrics_and_dashboard(
    run_id: str,
    final_metrics: Dict[str, Dict[str, Any]],
    profile_name: Optional[str] = None,
    namespace: str = 'LoadBalancerMetrics',
):
    """
    Publish summary metrics for each algorithm to CloudWatch and create a
    comparison dashboard. Expects final_metrics like:
      {
        'Round Robin': {'AvgResponseTime_s': ..., 'Throughput_task_s': ..., 'TotalEnergy_kJ': ..., 'Makespan_s': ...},
        'RHO': {...},
        'ACO': {...}
      }
    """
    session = _get_session(profile_name)
    cw = session.client('cloudwatch')

    # Compute PerformanceScore per algorithm
    perf_scores = _compute_performance_scores(final_metrics)

    # Prepare metric data
    metric_data = []
    def add_metric(algo: str, name: str, value: float, unit: str | None = None):
        datum = {
            'MetricName': name,
            'Dimensions': [
                {'Name': 'Algorithm', 'Value': algo},
                {'Name': 'RunID', 'Value': run_id},
            ],
            'Value': float(value),
        }
        if unit:
            datum['Unit'] = unit
        metric_data.append(datum)

    for algo, mets in final_metrics.items():
        if 'AvgResponseTime_s' in mets:
            add_metric(algo, 'AverageResponseTime', mets['AvgResponseTime_s'], 'Seconds')
        if 'Makespan_s' in mets:
            add_metric(algo, 'Makespan', mets['Makespan_s'], 'Seconds')
        if 'Throughput_task_s' in mets:
            # tasks per second
            add_metric(algo, 'Throughput', mets['Throughput_task_s'], 'Count/Second')
        if 'TotalEnergy_kJ' in mets:
            add_metric(algo, 'TotalEnergy', mets['TotalEnergy_kJ'], 'Kilojoules')
        if algo in perf_scores:
            add_metric(algo, 'PerformanceScore', perf_scores[algo], 'Percent')

    # Put metrics in batches of 20 (CloudWatch limit per call)
    for i in range(0, len(metric_data), 20):
        batch = metric_data[i:i+20]
        if batch:
            cw.put_metric_data(Namespace=namespace, MetricData=batch)

    # Build a comparison dashboard
    region = cw.meta.region_name
    algos = list(final_metrics.keys())

    def metric_rows(metric_name: str):
        return [[namespace, metric_name, 'Algorithm', a, 'RunID', run_id] for a in algos]

    dashboard = {
        'widgets': [
            {
                'type': 'metric', 'x': 0, 'y': 0, 'width': 12, 'height': 6,
                'properties': {
                    'metrics': metric_rows('AverageResponseTime'),
                    'view': 'bar', 'stacked': False, 'region': region,
                    'stat': 'Average', 'period': 60,
                    'title': 'Average Response Time (s) – lower is better'
                }
            },
            {
                'type': 'metric', 'x': 12, 'y': 0, 'width': 12, 'height': 6,
                'properties': {
                    'metrics': metric_rows('Throughput'),
                    'view': 'bar', 'stacked': False, 'region': region,
                    'stat': 'Average', 'period': 60,
                    'title': 'Throughput (tasks/sec) – higher is better'
                }
            },
            {
                'type': 'metric', 'x': 0, 'y': 6, 'width': 12, 'height': 6,
                'properties': {
                    'metrics': metric_rows('TotalEnergy'),
                    'view': 'bar', 'stacked': False, 'region': region,
                    'stat': 'Average', 'period': 60,
                    'title': 'Total Energy (kJ) – lower is better'
                }
            },
            {
                'type': 'metric', 'x': 12, 'y': 6, 'width': 12, 'height': 6,
                'properties': {
                    'metrics': metric_rows('PerformanceScore'),
                    'view': 'bar', 'stacked': False, 'region': region,
                    'stat': 'Average', 'period': 60,
                    'title': 'Overall Performance Score (0–100)'
                }
            }
        ]
    }

    cw.put_dashboard(
        DashboardName=f'Load_Balancer_Comparison_{run_id}',
        DashboardBody=__import__('json').dumps(dashboard)
    )

    return {
        'namespace': namespace,
        'region': region,
        'dashboard': f'Load_Balancer_Comparison_{run_id}',
    }
