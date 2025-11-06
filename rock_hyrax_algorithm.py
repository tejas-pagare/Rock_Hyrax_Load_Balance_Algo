"""
Rock Hyrax Load Balancing Algorithm

This module implements the Rock Hyrax optimization algorithm for load balancing,
inspired by the social behavior and foraging patterns of rock hyraxes.
"""

import random
import math
from typing import List, Dict, Tuple, Optional


class Server:
    """Represents a server/instance in the load balancing pool."""
    
    def __init__(self, server_id: str, capacity: float, current_load: float = 0.0):
        """
        Initialize a server.
        
        Args:
            server_id: Unique identifier for the server
            capacity: Maximum capacity of the server
            current_load: Current load on the server (default: 0.0)
        """
        self.server_id = server_id
        self.capacity = capacity
        self.current_load = current_load
        self.utilization = current_load / capacity if capacity > 0 else 0.0
    
    def add_load(self, load: float) -> bool:
        """
        Add load to the server.
        
        Args:
            load: Amount of load to add
            
        Returns:
            True if load was added successfully, False if it would exceed capacity
        """
        if self.current_load + load <= self.capacity:
            self.current_load += load
            self.utilization = self.current_load / self.capacity
            return True
        return False
    
    def remove_load(self, load: float) -> None:
        """Remove load from the server."""
        self.current_load = max(0, self.current_load - load)
        self.utilization = self.current_load / self.capacity if self.capacity > 0 else 0.0
    
    def get_available_capacity(self) -> float:
        """Get the available capacity of the server."""
        return self.capacity - self.current_load
    
    def __repr__(self) -> str:
        return f"Server(id={self.server_id}, utilization={self.utilization:.2%})"


class RockHyrax:
    """
    Represents a Rock Hyrax agent in the optimization algorithm.
    
    Rock hyraxes are social animals that use sentinel behavior and
    cooperative foraging. This class models their behavior for load balancing.
    """
    
    def __init__(self, position: List[int], fitness: float = float('inf')):
        """
        Initialize a Rock Hyrax agent.
        
        Args:
            position: Position in the solution space (server load distribution)
            fitness: Fitness value (lower is better)
        """
        self.position = position.copy()
        self.fitness = fitness
        self.best_position = position.copy()
        self.best_fitness = fitness


class RockHyraxLoadBalancer:
    """
    Rock Hyrax Load Balancing Algorithm implementation.
    
    This algorithm uses nature-inspired optimization based on rock hyrax behavior
    to efficiently distribute load across servers.
    """
    
    def __init__(
        self,
        servers: List[Server],
        population_size: int = 30,
        max_iterations: int = 100,
        alpha: float = 2.0,
        beta: float = 0.5
    ):
        """
        Initialize the Rock Hyrax Load Balancer.
        
        Args:
            servers: List of servers to balance load across
            population_size: Number of rock hyrax agents
            max_iterations: Maximum number of iterations
            alpha: Exploration parameter
            beta: Exploitation parameter
        """
        self.servers = servers
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.beta = beta
        self.population: List[RockHyrax] = []
        self.global_best_position: Optional[List[float]] = None
        self.global_best_fitness = float('inf')
    
    def initialize_population(self, tasks: List[float]) -> None:
        """
        Initialize the population of rock hyrax agents.
        
        Args:
            tasks: List of task loads to distribute
        """
        self.population = []
        num_servers = len(self.servers)
        
        for _ in range(self.population_size):
            # Random assignment of tasks to servers
            position = [random.randint(0, num_servers - 1) for _ in tasks]
            hyrax = RockHyrax(position)
            hyrax.fitness = self.calculate_fitness(position, tasks)
            hyrax.best_fitness = hyrax.fitness
            self.population.append(hyrax)
            
            # Update global best
            if hyrax.fitness < self.global_best_fitness:
                self.global_best_fitness = hyrax.fitness
                self.global_best_position = position.copy()
    
    def calculate_fitness(self, position: List[float], tasks: List[float]) -> float:
        """
        Calculate fitness of a solution (lower is better).
        
        The fitness is based on:
        1. Load imbalance across servers
        2. Maximum server utilization
        3. Number of overloaded servers
        
        Args:
            position: Assignment of tasks to servers
            tasks: List of task loads
            
        Returns:
            Fitness value (lower is better)
        """
        # Calculate load on each server
        server_loads = [0.0] * len(self.servers)
        for task_idx, server_idx in enumerate(position):
            server_loads[int(server_idx)] += tasks[task_idx]
        
        # Calculate fitness components
        max_load = max(server_loads) if server_loads else 0
        min_load = min(server_loads) if server_loads else 0
        avg_load = sum(server_loads) / len(server_loads) if server_loads else 0
        
        # Imbalance factor
        imbalance = max_load - min_load
        
        # Standard deviation of loads
        variance = sum((load - avg_load) ** 2 for load in server_loads) / len(server_loads)
        std_dev = math.sqrt(variance)
        
        # Penalty for exceeding capacity
        capacity_penalty = 0
        for idx, load in enumerate(server_loads):
            if load > self.servers[idx].capacity:
                capacity_penalty += (load - self.servers[idx].capacity) * 10
        
        # Combined fitness (lower is better)
        fitness = imbalance + std_dev + capacity_penalty
        
        return fitness
    
    def update_position(self, hyrax: RockHyrax, iteration: int, tasks: List[float]) -> None:
        """
        Update rock hyrax position using sentinel and foraging behavior.
        
        Args:
            hyrax: The rock hyrax agent to update
            iteration: Current iteration number
            tasks: List of task loads
        """
        num_servers = len(self.servers)
        new_position = hyrax.position.copy()
        
        # Decreasing exploration factor
        exploration_factor = self.alpha * (1 - iteration / self.max_iterations)
        
        for i in range(len(new_position)):
            # Sentinel behavior: Learn from global best
            if random.random() < 0.5:
                if self.global_best_position:
                    # Move toward global best with some randomness
                    if random.random() < self.beta:
                        new_position[i] = self.global_best_position[i]
                    else:
                        # Random exploration
                        new_position[i] = random.randint(0, num_servers - 1)
            else:
                # Foraging behavior: Local search
                if random.random() < exploration_factor:
                    # Random jump (exploration)
                    new_position[i] = random.randint(0, num_servers - 1)
                else:
                    # Local adjustment (exploitation)
                    adjustment = random.choice([-1, 0, 1])
                    new_position[i] = max(0, min(num_servers - 1, 
                                                  int(new_position[i] + adjustment)))
        
        # Update position if fitness improves
        new_fitness = self.calculate_fitness(new_position, tasks)
        if new_fitness < hyrax.fitness:
            hyrax.position = new_position
            hyrax.fitness = new_fitness
            
            # Update personal best
            if new_fitness < hyrax.best_fitness:
                hyrax.best_position = new_position.copy()
                hyrax.best_fitness = new_fitness
            
            # Update global best
            if new_fitness < self.global_best_fitness:
                self.global_best_fitness = new_fitness
                self.global_best_position = new_position.copy()
    
    def optimize(self, tasks: List[float]) -> Dict[str, any]:
        """
        Optimize load distribution using Rock Hyrax algorithm.
        
        Args:
            tasks: List of task loads to distribute
            
        Returns:
            Dictionary containing optimization results
        """
        # Initialize population
        self.initialize_population(tasks)
        
        # Optimization iterations
        for iteration in range(self.max_iterations):
            for hyrax in self.population:
                self.update_position(hyrax, iteration, tasks)
        
        # Build result
        task_assignments = {}
        if self.global_best_position:
            for task_idx, server_idx in enumerate(self.global_best_position):
                server_id = self.servers[int(server_idx)].server_id
                if server_id not in task_assignments:
                    task_assignments[server_id] = []
                task_assignments[server_id].append(task_idx)
        
        return {
            'assignments': task_assignments,
            'fitness': self.global_best_fitness,
            'position': self.global_best_position
        }
    
    def balance_load(self, tasks: List[float]) -> Dict[str, List[int]]:
        """
        Balance load across servers.
        
        Args:
            tasks: List of task loads to distribute
            
        Returns:
            Dictionary mapping server IDs to task indices
        """
        result = self.optimize(tasks)
        return result['assignments']
    
    def get_server_loads(self, tasks: List[float], assignments: Dict[str, List[int]]) -> Dict[str, float]:
        """
        Calculate total load on each server given assignments.
        
        Args:
            tasks: List of task loads
            assignments: Dictionary mapping server IDs to task indices
            
        Returns:
            Dictionary mapping server IDs to total loads
        """
        server_loads = {}
        for server_id, task_indices in assignments.items():
            total_load = sum(tasks[idx] for idx in task_indices)
            server_loads[server_id] = total_load
        return server_loads
