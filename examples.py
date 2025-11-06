"""
Example usage of Rock Hyrax Load Balancer with AWS integration
"""

from rock_hyrax_algorithm import Server, RockHyraxLoadBalancer
from aws_integration import AWSIntegration, AWSRockHyraxLoadBalancer
from config import config


def example_basic_load_balancing():
    """Example: Basic load balancing without AWS."""
    print("=" * 60)
    print("Example 1: Basic Rock Hyrax Load Balancing")
    print("=" * 60)
    
    # Create servers
    servers = [
        Server(server_id="server-1", capacity=100.0, current_load=20.0),
        Server(server_id="server-2", capacity=100.0, current_load=30.0),
        Server(server_id="server-3", capacity=100.0, current_load=10.0),
        Server(server_id="server-4", capacity=100.0, current_load=25.0),
    ]
    
    print(f"\nServers:")
    for server in servers:
        print(f"  {server}")
    
    # Create load balancer
    load_balancer = RockHyraxLoadBalancer(
        servers=servers,
        population_size=20,
        max_iterations=50
    )
    
    # Tasks to distribute
    tasks = [15.0, 20.0, 10.0, 25.0, 18.0, 12.0, 22.0, 16.0]
    print(f"\nTasks to distribute: {tasks}")
    print(f"Total task load: {sum(tasks)}")
    
    # Balance load
    assignments = load_balancer.balance_load(tasks)
    
    print(f"\nTask Assignments:")
    for server_id, task_indices in assignments.items():
        task_loads = [tasks[i] for i in task_indices]
        total_load = sum(task_loads)
        print(f"  {server_id}: tasks {task_indices} (total load: {total_load})")
    
    # Calculate final server loads
    server_loads = load_balancer.get_server_loads(tasks, assignments)
    print(f"\nFinal Server Loads:")
    for server in servers:
        assigned_load = server_loads.get(server.server_id, 0.0)
        total_load = server.current_load + assigned_load
        utilization = (total_load / server.capacity) * 100
        print(f"  {server.server_id}: {total_load:.2f}/{server.capacity:.2f} ({utilization:.1f}% utilization)")
    
    print()


def example_aws_integration():
    """Example: AWS integration with mock/simulated data."""
    print("=" * 60)
    print("Example 2: AWS Integration (Simulated)")
    print("=" * 60)
    
    print("\nNote: This example simulates AWS integration.")
    print("To use with real AWS resources, configure AWS credentials in .env file.")
    
    # For demonstration, we'll create servers manually
    # In real usage, these would come from AWS EC2 instances
    servers = [
        Server(server_id="i-0123456789abcdef0", capacity=100.0, current_load=15.0),
        Server(server_id="i-0123456789abcdef1", capacity=150.0, current_load=20.0),
        Server(server_id="i-0123456789abcdef2", capacity=100.0, current_load=10.0),
        Server(server_id="i-0123456789abcdef3", capacity=200.0, current_load=30.0),
    ]
    
    print(f"\nEC2 Instances (simulated):")
    for server in servers:
        print(f"  {server}")
    
    # Create load balancer
    load_balancer = RockHyraxLoadBalancer(
        servers=servers,
        population_size=config.population_size,
        max_iterations=config.max_iterations
    )
    
    # Simulated incoming tasks
    tasks = [20.0, 25.0, 15.0, 30.0, 18.0, 22.0, 16.0, 28.0, 14.0, 19.0]
    print(f"\nIncoming tasks: {tasks}")
    print(f"Total task load: {sum(tasks)}")
    
    # Balance load
    result = load_balancer.optimize(tasks)
    
    print(f"\nOptimization Results:")
    print(f"  Fitness score: {result['fitness']:.4f}")
    
    print(f"\nTask Assignments:")
    for server_id, task_indices in result['assignments'].items():
        task_loads = [tasks[i] for i in task_indices]
        total_load = sum(task_loads)
        print(f"  {server_id}: {len(task_indices)} tasks (total load: {total_load:.2f})")
    
    # Calculate final server loads
    server_loads = load_balancer.get_server_loads(tasks, result['assignments'])
    
    print(f"\nFinal Instance Loads:")
    for server in servers:
        assigned_load = server_loads.get(server.server_id, 0.0)
        total_load = server.current_load + assigned_load
        utilization = (total_load / server.capacity) * 100
        print(f"  {server.server_id}:")
        print(f"    Current: {server.current_load:.2f}, Assigned: {assigned_load:.2f}")
        print(f"    Total: {total_load:.2f}/{server.capacity:.2f} ({utilization:.1f}% utilization)")
    
    print()


def example_advanced_optimization():
    """Example: Advanced optimization with different server capacities."""
    print("=" * 60)
    print("Example 3: Advanced Optimization")
    print("=" * 60)
    
    # Create heterogeneous servers
    servers = [
        Server(server_id="small-1", capacity=50.0, current_load=10.0),
        Server(server_id="medium-1", capacity=100.0, current_load=20.0),
        Server(server_id="medium-2", capacity=100.0, current_load=15.0),
        Server(server_id="large-1", capacity=200.0, current_load=30.0),
        Server(server_id="large-2", capacity=200.0, current_load=25.0),
    ]
    
    print(f"\nHeterogeneous Server Pool:")
    for server in servers:
        print(f"  {server.server_id}: capacity={server.capacity}, current_load={server.current_load}")
    
    # Create load balancer with custom parameters
    load_balancer = RockHyraxLoadBalancer(
        servers=servers,
        population_size=40,
        max_iterations=100,
        alpha=2.5,
        beta=0.6
    )
    
    # Large set of tasks with varying sizes
    tasks = [
        10.0, 15.0, 20.0, 25.0, 12.0, 18.0, 22.0, 14.0, 16.0, 19.0,
        21.0, 13.0, 17.0, 23.0, 11.0, 24.0, 26.0, 9.0, 27.0, 8.0
    ]
    print(f"\nTasks to distribute: {len(tasks)} tasks")
    print(f"Task sizes: {tasks}")
    print(f"Total task load: {sum(tasks):.2f}")
    
    # Balance load
    result = load_balancer.optimize(tasks)
    
    print(f"\nOptimization Results:")
    print(f"  Fitness score: {result['fitness']:.4f}")
    print(f"  Iterations: {load_balancer.max_iterations}")
    
    # Calculate server loads
    server_loads = load_balancer.get_server_loads(tasks, result['assignments'])
    
    print(f"\nLoad Distribution:")
    total_capacity = sum(s.capacity for s in servers)
    total_load = sum(server_loads.values()) + sum(s.current_load for s in servers)
    
    for server in servers:
        assigned_load = server_loads.get(server.server_id, 0.0)
        total_server_load = server.current_load + assigned_load
        utilization = (total_server_load / server.capacity) * 100
        
        print(f"\n  {server.server_id}:")
        print(f"    Capacity: {server.capacity:.2f}")
        print(f"    Previous load: {server.current_load:.2f}")
        print(f"    New tasks: {assigned_load:.2f}")
        print(f"    Total load: {total_server_load:.2f}")
        print(f"    Utilization: {utilization:.1f}%")
        print(f"    Available: {server.capacity - total_server_load:.2f}")
    
    print(f"\nOverall Statistics:")
    print(f"  Total capacity: {total_capacity:.2f}")
    print(f"  Total load: {total_load:.2f}")
    print(f"  System utilization: {(total_load / total_capacity) * 100:.1f}%")
    
    print()


if __name__ == "__main__":
    # Run examples
    example_basic_load_balancing()
    example_aws_integration()
    example_advanced_optimization()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
