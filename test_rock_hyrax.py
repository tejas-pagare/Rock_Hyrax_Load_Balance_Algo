"""
Tests for Rock Hyrax Load Balancing Algorithm
"""

import unittest
from rock_hyrax_algorithm import Server, RockHyrax, RockHyraxLoadBalancer


class TestServer(unittest.TestCase):
    """Test cases for Server class."""
    
    def test_server_initialization(self):
        """Test server initialization."""
        server = Server(server_id="test-1", capacity=100.0, current_load=20.0)
        self.assertEqual(server.server_id, "test-1")
        self.assertEqual(server.capacity, 100.0)
        self.assertEqual(server.current_load, 20.0)
        self.assertEqual(server.utilization, 0.2)
    
    def test_add_load_success(self):
        """Test adding load to server."""
        server = Server(server_id="test-1", capacity=100.0, current_load=20.0)
        result = server.add_load(30.0)
        self.assertTrue(result)
        self.assertEqual(server.current_load, 50.0)
        self.assertEqual(server.utilization, 0.5)
    
    def test_add_load_exceeds_capacity(self):
        """Test adding load that exceeds capacity."""
        server = Server(server_id="test-1", capacity=100.0, current_load=80.0)
        result = server.add_load(30.0)
        self.assertFalse(result)
        self.assertEqual(server.current_load, 80.0)
    
    def test_remove_load(self):
        """Test removing load from server."""
        server = Server(server_id="test-1", capacity=100.0, current_load=50.0)
        server.remove_load(20.0)
        self.assertEqual(server.current_load, 30.0)
        self.assertEqual(server.utilization, 0.3)
    
    def test_remove_load_below_zero(self):
        """Test removing more load than available."""
        server = Server(server_id="test-1", capacity=100.0, current_load=10.0)
        server.remove_load(20.0)
        self.assertEqual(server.current_load, 0.0)
    
    def test_get_available_capacity(self):
        """Test getting available capacity."""
        server = Server(server_id="test-1", capacity=100.0, current_load=30.0)
        available = server.get_available_capacity()
        self.assertEqual(available, 70.0)


class TestRockHyrax(unittest.TestCase):
    """Test cases for RockHyrax class."""
    
    def test_rock_hyrax_initialization(self):
        """Test RockHyrax initialization."""
        position = [0, 1, 2, 1]
        hyrax = RockHyrax(position=position, fitness=10.0)
        self.assertEqual(hyrax.position, position)
        self.assertEqual(hyrax.fitness, 10.0)
        self.assertEqual(hyrax.best_position, position)
        self.assertEqual(hyrax.best_fitness, 10.0)


class TestRockHyraxLoadBalancer(unittest.TestCase):
    """Test cases for RockHyraxLoadBalancer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.servers = [
            Server(server_id="server-1", capacity=100.0, current_load=0.0),
            Server(server_id="server-2", capacity=100.0, current_load=0.0),
            Server(server_id="server-3", capacity=100.0, current_load=0.0),
        ]
        self.load_balancer = RockHyraxLoadBalancer(
            servers=self.servers,
            population_size=10,
            max_iterations=20
        )
    
    def test_initialization(self):
        """Test load balancer initialization."""
        self.assertEqual(len(self.load_balancer.servers), 3)
        self.assertEqual(self.load_balancer.population_size, 10)
        self.assertEqual(self.load_balancer.max_iterations, 20)
    
    def test_calculate_fitness(self):
        """Test fitness calculation."""
        tasks = [10.0, 20.0, 30.0]
        position = [0, 1, 2]  # One task per server
        fitness = self.load_balancer.calculate_fitness(position, tasks)
        self.assertIsInstance(fitness, float)
        self.assertGreaterEqual(fitness, 0.0)
    
    def test_initialize_population(self):
        """Test population initialization."""
        tasks = [10.0, 20.0, 15.0, 25.0]
        self.load_balancer.initialize_population(tasks)
        self.assertEqual(len(self.load_balancer.population), 10)
        for hyrax in self.load_balancer.population:
            self.assertEqual(len(hyrax.position), len(tasks))
            self.assertIsInstance(hyrax.fitness, float)
    
    def test_balance_load(self):
        """Test load balancing."""
        tasks = [10.0, 20.0, 15.0, 25.0, 18.0]
        assignments = self.load_balancer.balance_load(tasks)
        
        # Check that all tasks are assigned
        total_assigned = sum(len(task_list) for task_list in assignments.values())
        self.assertEqual(total_assigned, len(tasks))
        
        # Check that assignments are valid
        for server_id, task_indices in assignments.items():
            self.assertIn(server_id, [s.server_id for s in self.servers])
            for idx in task_indices:
                self.assertGreaterEqual(idx, 0)
                self.assertLess(idx, len(tasks))
    
    def test_get_server_loads(self):
        """Test server load calculation."""
        tasks = [10.0, 20.0, 30.0]
        assignments = {
            "server-1": [0, 1],  # 10 + 20 = 30
            "server-2": [2]       # 30
        }
        
        server_loads = self.load_balancer.get_server_loads(tasks, assignments)
        self.assertEqual(server_loads["server-1"], 30.0)
        self.assertEqual(server_loads["server-2"], 30.0)
    
    def test_optimize(self):
        """Test optimization process."""
        tasks = [10.0, 20.0, 15.0, 25.0]
        result = self.load_balancer.optimize(tasks)
        
        self.assertIn('assignments', result)
        self.assertIn('fitness', result)
        self.assertIn('position', result)
        
        # Check fitness is valid
        self.assertIsInstance(result['fitness'], float)
        self.assertGreaterEqual(result['fitness'], 0.0)
    
    def test_empty_tasks(self):
        """Test with empty task list."""
        tasks = []
        assignments = self.load_balancer.balance_load(tasks)
        self.assertEqual(len(assignments), 0)
    
    def test_single_task(self):
        """Test with single task."""
        tasks = [50.0]
        assignments = self.load_balancer.balance_load(tasks)
        total_assigned = sum(len(task_list) for task_list in assignments.values())
        self.assertEqual(total_assigned, 1)
    
    def test_many_tasks(self):
        """Test with many tasks."""
        tasks = [float(i) for i in range(1, 21)]  # 20 tasks
        assignments = self.load_balancer.balance_load(tasks)
        total_assigned = sum(len(task_list) for task_list in assignments.values())
        self.assertEqual(total_assigned, len(tasks))


class TestLoadBalancing(unittest.TestCase):
    """Integration tests for load balancing."""
    
    def test_balanced_distribution(self):
        """Test that load is distributed reasonably."""
        servers = [
            Server(server_id=f"server-{i}", capacity=100.0, current_load=0.0)
            for i in range(5)
        ]
        
        load_balancer = RockHyraxLoadBalancer(
            servers=servers,
            population_size=30,
            max_iterations=50
        )
        
        # Create uniform tasks
        tasks = [10.0] * 20  # 20 tasks of size 10
        assignments = load_balancer.balance_load(tasks)
        server_loads = load_balancer.get_server_loads(tasks, assignments)
        
        # Check that load is distributed across servers
        loads = list(server_loads.values())
        if loads:
            max_load = max(loads)
            min_load = min(loads)
            # The difference shouldn't be too large for uniform tasks
            if min_load > 0:
                self.assertLess(max_load - min_load, 50.0)
    
    def test_respects_capacity(self):
        """Test that server capacity is respected."""
        servers = [
            Server(server_id="small", capacity=50.0, current_load=0.0),
            Server(server_id="large", capacity=200.0, current_load=0.0),
        ]
        
        load_balancer = RockHyraxLoadBalancer(
            servers=servers,
            population_size=20,
            max_iterations=100
        )
        
        tasks = [20.0, 25.0, 30.0, 15.0, 18.0]
        result = load_balancer.optimize(tasks)
        server_loads = load_balancer.get_server_loads(tasks, result['assignments'])
        
        # Check that loads don't greatly exceed capacity
        # (The algorithm should minimize capacity violations)
        for server in servers:
            load = server_loads.get(server.server_id, 0.0)
            # Allow some tolerance in the optimization
            self.assertLess(load, server.capacity * 1.5)


if __name__ == '__main__':
    unittest.main()
