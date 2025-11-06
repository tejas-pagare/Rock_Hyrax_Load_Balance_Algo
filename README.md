# Rock Hyrax Load Balancing Algorithm with AWS Integration

A nature-inspired load balancing algorithm based on the social behavior and foraging patterns of rock hyraxes, with full AWS integration for dynamic cloud infrastructure management.

## Overview

This project implements the Rock Hyrax optimization algorithm for intelligent load balancing across distributed systems. Rock hyraxes are small mammals known for their cooperative behavior and efficient foraging strategies, which inspire this algorithm's approach to resource distribution.

### Key Features

- **Nature-Inspired Optimization**: Uses sentinel and foraging behaviors of rock hyraxes for efficient load distribution
- **AWS Integration**: Seamless integration with AWS EC2 and ELB services
- **Dynamic Load Balancing**: Real-time load distribution across heterogeneous server pools
- **Configurable Parameters**: Customizable population size, iterations, and algorithm parameters
- **CloudWatch Metrics**: Integration with AWS CloudWatch for monitoring instance utilization
- **Target Group Management**: Automatic registration/deregistration of instances with ELB target groups

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tejas-pagare/Rock_Hyrax_Load_Balance_Algo.git
cd Rock_Hyrax_Load_Balance_Algo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials (optional, for AWS integration):
```bash
cp .env.example .env
# Edit .env and add your AWS credentials
```

## Usage

### Basic Load Balancing (Without AWS)

```python
from rock_hyrax_algorithm import Server, RockHyraxLoadBalancer

# Create servers
servers = [
    Server(server_id="server-1", capacity=100.0, current_load=20.0),
    Server(server_id="server-2", capacity=100.0, current_load=30.0),
    Server(server_id="server-3", capacity=100.0, current_load=10.0),
]

# Create load balancer
load_balancer = RockHyraxLoadBalancer(
    servers=servers,
    population_size=30,
    max_iterations=100
)

# Tasks to distribute
tasks = [15.0, 20.0, 10.0, 25.0, 18.0]

# Balance load
assignments = load_balancer.balance_load(tasks)
print(f"Task assignments: {assignments}")

# Get server loads
server_loads = load_balancer.get_server_loads(tasks, assignments)
print(f"Server loads: {server_loads}")
```

### AWS Integration

```python
from aws_integration import AWSIntegration, AWSRockHyraxLoadBalancer
from config import config

# Initialize AWS integration
aws = AWSIntegration(
    region_name=config.aws_region,
    aws_access_key_id=config.aws_access_key_id,
    aws_secret_access_key=config.aws_secret_access_key
)

# Create AWS-integrated load balancer
lb = AWSRockHyraxLoadBalancer(
    aws_integration=aws,
    population_size=30,
    max_iterations=100
)

# Refresh servers from AWS
lb.refresh_servers()

# Balance tasks
tasks = [20.0, 25.0, 15.0, 30.0, 18.0]
result = lb.balance_tasks(tasks)

print(f"Optimization results: {result}")
```

### Running Examples

```bash
python examples.py
```

This will run three example scenarios:
1. Basic load balancing without AWS
2. Simulated AWS integration
3. Advanced optimization with heterogeneous servers

## Algorithm Details

### Rock Hyrax Behavior

The algorithm is inspired by two key behaviors of rock hyraxes:

1. **Sentinel Behavior**: Rock hyraxes post sentinels to watch for predators while others forage. This translates to global best solution tracking and exploitation.

2. **Foraging Behavior**: Cooperative foraging strategies that balance exploration and exploitation, similar to the algorithm's balance between searching new solutions and refining existing ones.

### Algorithm Parameters

- `population_size`: Number of rock hyrax agents (default: 30)
- `max_iterations`: Maximum optimization iterations (default: 100)
- `alpha`: Exploration parameter (default: 2.0)
- `beta`: Exploitation parameter (default: 0.5)

### Fitness Function

The fitness function minimizes:
- Load imbalance across servers
- Standard deviation of server loads
- Capacity constraint violations

## AWS Components

### Supported Services

- **EC2**: Dynamic instance discovery and metrics collection
- **ELB (Elastic Load Balancer)**: Target group management
- **CloudWatch**: Instance utilization monitoring

### Instance Capacity Calculation

Instance capacity is automatically calculated based on instance type and a configurable multiplier. Supported instance types include:
- t2/t3 family (micro, small, medium, large)
- m5 family (large, xlarge, 2xlarge)
- c5 family (large, xlarge, 2xlarge)

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Algorithm Configuration
POPULATION_SIZE=30
MAX_ITERATIONS=100
ALPHA=2.0
BETA=0.5

# Instance Configuration
CAPACITY_MULTIPLIER=100.0
DEFAULT_PORT=80

# Logging
LOG_LEVEL=INFO
```

## Testing

Run the test suite:

```bash
python -m pytest test_rock_hyrax.py -v
```

Or using unittest:

```bash
python -m unittest test_rock_hyrax.py
```

## Architecture

```
rock_hyrax_algorithm.py    # Core algorithm implementation
├── Server                  # Server/instance representation
├── RockHyrax              # Rock hyrax agent
└── RockHyraxLoadBalancer  # Main load balancing algorithm

aws_integration.py         # AWS service integration
├── AWSIntegration         # AWS API wrapper
└── AWSRockHyraxLoadBalancer  # AWS-enabled load balancer

config.py                  # Configuration management
examples.py                # Usage examples
test_rock_hyrax.py        # Test suite
```

## Performance Characteristics

- **Time Complexity**: O(P × I × N × S) where:
  - P = population size
  - I = iterations
  - N = number of tasks
  - S = number of servers

- **Space Complexity**: O(P × N) for population storage

- **Convergence**: Typically converges within 50-100 iterations for most scenarios

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source and available under the MIT License.

## References

- Rock Hyrax Optimization Algorithm: Nature-inspired metaheuristic optimization
- AWS SDK for Python (Boto3): https://boto3.amazonaws.com/
- Load Balancing Algorithms: Survey and comparative analysis

## Author

Tejas Pagare

## Acknowledgments

- Inspired by nature-inspired optimization algorithms
- Built with AWS SDK for Python (Boto3)
- Thanks to the open-source community