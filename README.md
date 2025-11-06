Cloud Load Balancing Simulation (RR, RHO, ACO)

This project simulates and compares three load balancing algorithms (Round Robin, Rock Hyrax Optimization, and Ant Colony Optimization) in a heterogeneous cloud environment.

It is designed to run locally or in a cloud environment (like AWS EC2), with built-in integration to log results to AWS DynamoDB and upload graph artifacts to AWS S3.

Project Structure

.
├── main.py                     # Main entry point
├── simulation.py               # Core experiment logic
├── entities.py                 # VM and Task definitions
├── config.py                   # Default simulation parameters
├── interactive.py              # Interactive user prompts
├── metrics.py                  # Metric calculation & printing
├── plotting.py                 # .png graph generation
├── aws_utils.py                # AWS DynamoDB & S3 integration
├── README.md                   # This readme file
├── requirements.txt            # Python dependencies
└── algorithms/                 # Directory for algorithm classes
    ├── base.py
    ├── round_robin.py
    ├── rho.py
    └── aco.py


Local Execution

1. Setup

Clone/Download: Get all the project files into a single directory.

Create a Virtual Environment (Recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:

pip install -r requirements.txt


2. Run

Run with default parameters:

python main.py


This will prompt you to use default or custom parameters.

Run and skip prompts (use defaults):

python main.py --skip-interactive


The script will run the full simulation and generate load_distribution.png, metrics_comparison.png, and performance_graphs.png in the same directory.

AWS Execution & Setup

This guide assumes you have an AWS account and the AWS CLI installed and configured.

1. AWS Prerequisite Setup

Create an IAM User:

Go to the IAM service in your AWS console.

Create a new user.

Attach the following policies:

AmazonDynamoDBFullAccess

AmazonS3FullAccess

(Security Note): For production, you should create custom policies with permissions scoped only to the required table and bucket.

Create access keys for this user and configure your environment with them (aws configure).

Create DynamoDB Table:

You must create the table manually before the first run.

Run this AWS CLI command, replacing YourTableName with the name you want (e.g., LoadBalancingSimResults).

aws dynamodb create-table \
    --table-name LoadBalancingSimResults \
    --attribute-definitions \
        AttributeName=RunID,AttributeType=S \
        AttributeName=AlgorithmTaskCount,AttributeType=S \
    --key-schema \
        AttributeName=RunID,KeyType=HASH \
        AttributeName=AlgorithmTaskCount,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST


The default table name in the script is LoadBalancingSimResults.

Create S3 Bucket:

Go to the S3 service in your AWS console.

Create a new, private S3 bucket (e.g., my-load-balancing-graphs). Remember its name.

2. Run with AWS Integration

Now you can run the script with the AWS flags.

--aws-enabled: Turns on the AWS logging.

--dynamo-table: The name of the table you created (defaults to LoadBalancingSimResults).

--s3-bucket: The name of the S3 bucket you created (e.g., my-load-balancing-graphs).

--aws-profile (Optional): If you use a specific AWS CLI profile.

Example Command:

python main.py --skip-interactive \
               --aws-enabled \
               --s3-bucket my-load-balancing-graphs \
               --dynamo-table LoadBalancingSimResults


3. What Happens

When you run with AWS enabled, the script will:

Clear DynamoDB: It will scan and delete all items from the LoadBalancingSimResults table (as you requested).

Run Simulation: It runs the full experiment locally.

Log to DynamoDB: It populates the table with all metrics from the new run, tagged with a unique RunID.

Upload to S3: It uploads the three .png graphs to your S3 bucket under a "folder" named after the RunID (e.g., s3://my-load-balancing-graphs/sim-run-2025-11-07.../).

You can then view the .png files in the S3 console and query the raw data in the DynamoDB console.# Rock_Hyrax_Load_Balance_Algo