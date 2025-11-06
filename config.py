"""
Configuration management for Rock Hyrax Load Balancer
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Rock Hyrax Load Balancer."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # AWS Configuration
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Algorithm Configuration
        self.population_size = int(os.getenv('POPULATION_SIZE', '30'))
        self.max_iterations = int(os.getenv('MAX_ITERATIONS', '100'))
        self.alpha = float(os.getenv('ALPHA', '2.0'))
        self.beta = float(os.getenv('BETA', '0.5'))
        
        # Instance Configuration
        self.capacity_multiplier = float(os.getenv('CAPACITY_MULTIPLIER', '100.0'))
        self.default_port = int(os.getenv('DEFAULT_PORT', '80'))
        
        # Logging Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary containing all configuration values
        """
        return {
            'aws_region': self.aws_region,
            'population_size': self.population_size,
            'max_iterations': self.max_iterations,
            'alpha': self.alpha,
            'beta': self.beta,
            'capacity_multiplier': self.capacity_multiplier,
            'default_port': self.default_port,
            'log_level': self.log_level
        }
    
    def get_aws_credentials(self) -> Dict[str, Optional[str]]:
        """
        Get AWS credentials.
        
        Returns:
            Dictionary containing AWS credentials
        """
        return {
            'region_name': self.aws_region,
            'aws_access_key_id': self.aws_access_key_id,
            'aws_secret_access_key': self.aws_secret_access_key
        }


# Global configuration instance
config = Config()
