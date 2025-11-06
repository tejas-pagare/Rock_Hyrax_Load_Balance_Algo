import matplotlib.pyplot as plt
import numpy as np

def plot_single_run_results(finish_times_dict, metrics_dict, num_vms):
    """
    Generates bar charts to visually compare the load distribution
    and overall metrics for a single simulation run.
    """
    vm_ids = [f"VM {i}" for i in range(num_vms)]
    algorithms = list(finish_times_dict.keys())
    num_algos = len(algorithms)
    
    # --- Plot 1: Load Distribution (Finish Time per VM) ---
    plt.figure(figsize=(18, 7))
    
    x = np.arange(num_vms)
    width = 0.8 / num_algos # Make bars thinner to fit
    
    colors = ['skyblue', 'darkorange', 'green']
    
    for i, (algo, times) in enumerate(finish_times_dict.items()):
        offset = (i - (num_algos - 1) / 2) * width
        plt.bar(x + offset, times, width, label=algo, color=colors[i % len(colors)])
    
    plt.ylabel('VM Finish Time (seconds)')
    plt.title('Load Distribution Comparison (for Max Tasks)')
    plt.xticks(x, vm_ids, rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    graph_file_1 = 'load_distribution.png'
    plt.savefig(graph_file_1)
    
    # --- Plot 2: Metrics Comparison ---
    metrics_to_plot = list(metrics_dict[algorithms[0]].keys())
    
    plt.figure(figsize=(15, 7))
    
    x = np.arange(len(metrics_to_plot))
    width = 0.8 / num_algos
    
    for i, algo in enumerate(algorithms):
        values = [metrics_dict[algo][key] for key in metrics_to_plot]
        offset = (i - (num_algos - 1) / 2) * width
        plt.bar(x + offset, values, width, label=algo, color=colors[i % len(colors)])
    
    plt.ylabel('Value')
    plt.title('Key Performance Metrics Comparison (for Max Tasks)')
    plt.xticks(x, [k.replace('_', ' ') for k in metrics_to_plot], rotation=15)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    graph_file_2 = 'metrics_comparison.png'
    plt.savefig(graph_file_2)
    
    plt.close('all')
    return [graph_file_1, graph_file_2]

def plot_experiment_graphs(results_log):
    """
    Generates line graphs showing how metrics change as the
    number of tasks increases, comparing all algorithms.
    """
    task_counts = sorted(results_log.keys())
    if not task_counts:
        return None
        
    # Get metrics from the first task count's RR data
    sample_metrics = results_log[task_counts[0]]['Round Robin']
    metrics = list(sample_metrics.keys())
    
    # Create a 2x2 grid for the plots
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Performance Comparison vs. Number of Tasks', fontsize=16)
    
    # Flatten axs for easy iteration
    axs = axs.flatten()
    colors = ['skyblue', 'darkorange', 'green']
    markers = ['o', 's', 'd']
    algos = ["Round Robin", "RHO", "ACO"]
    
    for i, metric in enumerate(metrics):
        # Collect data for each algorithm
        data_to_plot = {algo: [] for algo in algos}
        for tc in task_counts:
            for algo in algos:
                data_to_plot[algo].append(results_log[tc][algo][metric])

        # Plot all three
        for j, algo in enumerate(algos):
            axs[i].plot(task_counts, data_to_plot[algo], marker=markers[j], linestyle='-', label=algo, color=colors[j])
        
        metric_label = metric.replace('_', ' ').replace(' s', '(s)').replace('task s', '(tasks/s)').replace('kJ', '(kJ)')
        axs[i].set_title(f'{metric_label} vs. Number of Tasks')
        axs[i].set_xlabel('Number of Tasks')
        axs[i].set_ylabel(metric_label)
        axs[i].legend()
        axs[i].grid(True, linestyle='--', alpha=0.6)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    graph_file = 'performance_graphs.png'
    plt.savefig(graph_file)
    plt.close('all')
    return graph_file

def generate_all_plots(final_times, final_metrics, num_vms, experiment_results):
    """Generates all plots and returns a list of filenames."""
    files = []
    
    bar_files = plot_single_run_results(final_times, final_metrics, num_vms)
    files.extend(bar_files)
    
    line_file = plot_experiment_graphs(experiment_results)
    if line_file:
        files.append(line_file)
        
    return files