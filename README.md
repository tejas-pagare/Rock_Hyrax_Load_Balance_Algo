☁️ Cloud Load Balancing Simulation (RR, RHO, ACO)

This project simulates and compares three cloud load balancing algorithms —
Round Robin (RR), Rock Hyrax Optimization (RHO), and Ant Colony Optimization (ACO) —
within a heterogeneous cloud environment.

It supports both local and cloud-based execution (e.g., on AWS EC2), and includes integrated AWS logging:

DynamoDB → Stores simulation metrics

S3 → Uploads generated performance and load distribution graphs

🧠 Features

Simulation of three advanced load balancing algorithms (RR, RHO, ACO)

Comparison of algorithm performance using visual metrics and graphs

Dynamic VM and task generation for heterogeneous cloud environments

AWS integration for real-time storage and analysis

Command-line options for flexible execution (interactive or automated)

📁 Project Structure
.
├── main.py                     # Main entry point
├── simulation.py               # Core experiment logic
├── entities.py                 # VM and Task definitions
├── config.py                   # Default simulation parameters
├── interactive.py              # Interactive user prompt handler
├── metrics.py                  # Metric calculation & result printing
├── plotting.py                 # Graph generation (.png)
├── aws_utils.py                # AWS DynamoDB & S3 integration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── algorithms/                 # Algorithm implementations
    ├── base.py
    ├── round_robin.py
    ├── rho.py
    └── aco.py

⚙️ Local Execution
1. Setup

Clone the repository:

git clone https://github.com/tejas-pagare/Rock_Hyrax_Load_Balance_Algo.git
cd Rock_Hyrax_Load_Balance_Algo


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt

2. Run the Simulation

Run with default parameters:

python main.py


You’ll be prompted to use default or custom parameters.

To skip prompts and run directly with defaults:

python main.py --skip-interactive


After completion, the script generates:

load_distribution.png

metrics_comparison.png

performance_graphs.png

These graphs visualize task allocation, performance, and efficiency comparisons.

☁️ AWS Execution & Integration

💡 Note: Ensure you have an AWS account and the AWS CLI installed and configured (aws configure).

1. AWS Setup
Create an IAM User

Open the IAM service in AWS Console.

Create a new user and attach the following policies:

AmazonDynamoDBFullAccess

AmazonS3FullAccess
(Security note: For production, restrict access to specific resources only.)

Generate access keys and configure them via:

aws configure

Create a DynamoDB Table

Before the first run, create a table to store simulation results:

aws dynamodb create-table \
    --table-name LoadBalancingSimResults \
    --attribute-definitions \
        AttributeName=RunID,AttributeType=S \
        AttributeName=AlgorithmTaskCount,AttributeType=S \
    --key-schema \
        AttributeName=RunID,KeyType=HASH \
        AttributeName=AlgorithmTaskCount,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

Create an S3 Bucket

Go to the S3 console.

Create a new private bucket (e.g., my-load-balancing-graphs).

Note the bucket name — you’ll need it for the run command.

2. Run with AWS Integration

Use the following command:

python main.py --skip-interactive \
               --aws-enabled \
               --s3-bucket my-load-balancing-graphs \
               --dynamo-table LoadBalancingSimResults


Optional:

--aws-profile: Specify a custom AWS CLI profile.

3. AWS Workflow Overview

When AWS integration is enabled, the program:

Clears DynamoDB: Deletes previous run entries from the table.

Runs Simulation: Executes all three algorithms locally.

Logs Metrics: Uploads detailed results to DynamoDB under a unique RunID.

Uploads Graphs: Stores .png result files to your S3 bucket under:

s3://my-load-balancing-graphs/sim-run-2025-11-07.../


You can then view:

Metrics and timestamps in DynamoDB Console

Visual performance graphs in S3 Console

📊 Output Overview
File Name	Description
load_distribution.png	Task allocation across VMs
metrics_comparison.png	Comparative metrics (latency, throughput, etc.)
performance_graphs.png	Consolidated performance visualization
🧩 Algorithms Overview
Algorithm	Description	Characteristics
Round Robin (RR)	Sequential task assignment	Simple, equal distribution, no optimization
Rock Hyrax Optimization (RHO)	Nature-inspired metaheuristic	Adaptive, considers load and energy balance
Ant Colony Optimization (ACO)	Probabilistic optimization using pheromone trails	Efficient path selection, dynamic balancing
🧠 Future Improvements

Integration with container-based simulation (Docker + Kubernetes)

Real-time visualization dashboard (Streamlit)

Extended support for hybrid and edge-cloud environments

Cost-aware and energy-efficient task scheduling extensions

👨‍💻 Author

Pagre Tejas Kiran
Indian Institute of Information Technology, Sri City
📧 tejaspagare.work@gmail.com

🌐 GitHub: tejas-pagare

🏷️ License

This project is licensed under the MIT License — see the LICENSE
 file for details.
