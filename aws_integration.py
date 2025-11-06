"""
AWS Integration for Rock Hyrax Load Balancer

This module provides integration with AWS services (EC2, ELB) to enable
dynamic load balancing across AWS infrastructure.
"""

import boto3
from typing import List, Dict, Optional, Any
from botocore.exceptions import ClientError, BotoCoreError
import logging
from datetime import datetime, timedelta

from rock_hyrax_algorithm import Server, RockHyraxLoadBalancer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AWSIntegration:
    """AWS integration for Rock Hyrax load balancing."""
    
    def __init__(
        self,
        region_name: str = 'us-east-1',
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize AWS integration.
        
        Args:
            region_name: AWS region name
            aws_access_key_id: AWS access key ID (optional, uses default credentials if not provided)
            aws_secret_access_key: AWS secret access key (optional)
        """
        self.region_name = region_name
        
        # Initialize boto3 clients
        session_kwargs = {'region_name': region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs['aws_access_key_id'] = aws_access_key_id
            session_kwargs['aws_secret_access_key'] = aws_secret_access_key
        
        self.ec2_client = boto3.client('ec2', **session_kwargs)
        self.elb_client = boto3.client('elbv2', **session_kwargs)
        self.cloudwatch_client = boto3.client('cloudwatch', **session_kwargs)
    
    def get_ec2_instances(self, filters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Get EC2 instances from AWS.
        
        Args:
            filters: Optional filters for EC2 instances
            
        Returns:
            List of EC2 instance dictionaries
        """
        try:
            if filters is None:
                filters = [
                    {
                        'Name': 'instance-state-name',
                        'Values': ['running']
                    }
                ]
            
            response = self.ec2_client.describe_instances(Filters=filters)
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append(instance)
            
            logger.info(f"Found {len(instances)} EC2 instances")
            return instances
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error fetching EC2 instances: {e}")
            return []
    
    def get_instance_metrics(self, instance_id: str) -> Dict[str, float]:
        """
        Get CloudWatch metrics for an EC2 instance.
        
        Args:
            instance_id: EC2 instance ID
            
        Returns:
            Dictionary containing CPU utilization and other metrics
        """
        try:
            # Get CPU utilization
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=['Average']
            )
            
            cpu_utilization = 0.0
            if response['Datapoints']:
                cpu_utilization = response['Datapoints'][-1]['Average']
            
            return {
                'cpu_utilization': cpu_utilization,
                'instance_id': instance_id
            }
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error fetching metrics for instance {instance_id}: {e}")
            return {'cpu_utilization': 0.0, 'instance_id': instance_id}
    
    def create_servers_from_instances(
        self,
        instances: Optional[List[Dict[str, Any]]] = None,
        capacity_multiplier: float = 100.0
    ) -> List[Server]:
        """
        Create Server objects from EC2 instances.
        
        Args:
            instances: List of EC2 instances (fetched if not provided)
            capacity_multiplier: Multiplier for instance capacity calculation
            
        Returns:
            List of Server objects
        """
        if instances is None:
            instances = self.get_ec2_instances()
        
        servers = []
        for instance in instances:
            instance_id = instance['InstanceId']
            instance_type = instance.get('InstanceType', 't2.micro')
            
            # Get current metrics
            metrics = self.get_instance_metrics(instance_id)
            current_load = metrics['cpu_utilization']
            
            # Calculate capacity based on instance type
            capacity = self._calculate_instance_capacity(instance_type, capacity_multiplier)
            
            server = Server(
                server_id=instance_id,
                capacity=capacity,
                current_load=current_load
            )
            servers.append(server)
            
            logger.info(f"Created server: {server}")
        
        return servers
    
    def _calculate_instance_capacity(self, instance_type: str, multiplier: float) -> float:
        """
        Calculate instance capacity based on instance type.
        
        Args:
            instance_type: EC2 instance type
            multiplier: Capacity multiplier
            
        Returns:
            Calculated capacity
        """
        # Simplified capacity calculation based on instance type
        # In a real implementation, this would use actual vCPU and memory specs
        capacity_map = {
            't2.micro': 1.0,
            't2.small': 2.0,
            't2.medium': 4.0,
            't2.large': 8.0,
            't3.micro': 1.5,
            't3.small': 2.5,
            't3.medium': 5.0,
            't3.large': 10.0,
            'm5.large': 10.0,
            'm5.xlarge': 20.0,
            'm5.2xlarge': 40.0,
            'c5.large': 12.0,
            'c5.xlarge': 24.0,
            'c5.2xlarge': 48.0,
        }
        
        base_capacity = capacity_map.get(instance_type, 5.0)
        return base_capacity * multiplier
    
    def get_target_group_targets(self, target_group_arn: str) -> List[Dict[str, Any]]:
        """
        Get targets from an ELB target group.
        
        Args:
            target_group_arn: ARN of the target group
            
        Returns:
            List of target dictionaries
        """
        try:
            response = self.elb_client.describe_target_health(
                TargetGroupArn=target_group_arn
            )
            
            targets = response.get('TargetHealthDescriptions', [])
            logger.info(f"Found {len(targets)} targets in target group")
            return targets
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error fetching target group targets: {e}")
            return []
    
    def register_targets(
        self,
        target_group_arn: str,
        instance_ids: List[str],
        port: int = 80
    ) -> bool:
        """
        Register EC2 instances with a target group.
        
        Args:
            target_group_arn: ARN of the target group
            instance_ids: List of instance IDs to register
            port: Port number (default: 80)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            targets = [
                {'Id': instance_id, 'Port': port}
                for instance_id in instance_ids
            ]
            
            self.elb_client.register_targets(
                TargetGroupArn=target_group_arn,
                Targets=targets
            )
            
            logger.info(f"Registered {len(instance_ids)} targets to target group")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error registering targets: {e}")
            return False
    
    def deregister_targets(
        self,
        target_group_arn: str,
        instance_ids: List[str]
    ) -> bool:
        """
        Deregister EC2 instances from a target group.
        
        Args:
            target_group_arn: ARN of the target group
            instance_ids: List of instance IDs to deregister
            
        Returns:
            True if successful, False otherwise
        """
        try:
            targets = [{'Id': instance_id} for instance_id in instance_ids]
            
            self.elb_client.deregister_targets(
                TargetGroupArn=target_group_arn,
                Targets=targets
            )
            
            logger.info(f"Deregistered {len(instance_ids)} targets from target group")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error deregistering targets: {e}")
            return False


class AWSRockHyraxLoadBalancer:
    """
    Complete AWS-integrated Rock Hyrax load balancer.
    
    This class combines the Rock Hyrax algorithm with AWS services
    to provide intelligent load balancing across EC2 instances.
    """
    
    def __init__(
        self,
        aws_integration: AWSIntegration,
        population_size: int = 30,
        max_iterations: int = 100
    ):
        """
        Initialize AWS Rock Hyrax load balancer.
        
        Args:
            aws_integration: AWSIntegration instance
            population_size: Population size for the algorithm
            max_iterations: Maximum iterations for optimization
        """
        self.aws_integration = aws_integration
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.servers: List[Server] = []
        self.load_balancer: Optional[RockHyraxLoadBalancer] = None
    
    def refresh_servers(self, filters: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Refresh server list from AWS.
        
        Args:
            filters: Optional filters for EC2 instances
        """
        instances = self.aws_integration.get_ec2_instances(filters)
        self.servers = self.aws_integration.create_servers_from_instances(instances)
        
        # Create new load balancer with updated servers
        if self.servers:
            self.load_balancer = RockHyraxLoadBalancer(
                servers=self.servers,
                population_size=self.population_size,
                max_iterations=self.max_iterations
            )
    
    def balance_tasks(self, tasks: List[float]) -> Dict[str, Any]:
        """
        Balance tasks across AWS instances.
        
        Args:
            tasks: List of task loads to distribute
            
        Returns:
            Dictionary containing load balancing results
        """
        if not self.load_balancer:
            raise ValueError("No servers available. Call refresh_servers() first.")
        
        # Optimize task distribution
        result = self.load_balancer.optimize(tasks)
        
        # Calculate server loads
        server_loads = self.load_balancer.get_server_loads(tasks, result['assignments'])
        
        return {
            'assignments': result['assignments'],
            'server_loads': server_loads,
            'fitness': result['fitness'],
            'servers': [
                {
                    'id': server.server_id,
                    'capacity': server.capacity,
                    'current_load': server.current_load,
                    'utilization': server.utilization,
                    'assigned_load': server_loads.get(server.server_id, 0.0)
                }
                for server in self.servers
            ]
        }
    
    def apply_to_target_group(
        self,
        assignments: Dict[str, List[int]],
        target_group_arn: str,
        port: int = 80
    ) -> bool:
        """
        Apply load balancing assignments to an AWS target group.
        
        Args:
            assignments: Task assignments from load balancing
            target_group_arn: ARN of the target group
            port: Port number (default: 80)
            
        Returns:
            True if successful, False otherwise
        """
        # Get instance IDs that have tasks assigned
        instance_ids = list(assignments.keys())
        
        # Register instances with target group
        return self.aws_integration.register_targets(
            target_group_arn=target_group_arn,
            instance_ids=instance_ids,
            port=port
        )
