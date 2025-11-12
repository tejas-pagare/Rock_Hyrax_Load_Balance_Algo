# Cloud Load Balancing Simulation (RR • RHO • ACO)

Simulate and compare three load-balancing algorithms—Round Robin (RR), Rock Hyrax Optimization (RHO), and Ant Colony Optimization (ACO)—in a heterogeneous cloud environment. Run locally or on a cloud VM (e.g., AWS EC2), and optionally log results to AWS DynamoDB and upload plots to AWS S3.

---

## Table of Contents

- Overview
- Features
- Project Structure
- Prerequisites
- Quick Start
- Usage
    - Interactive mode
    - Non-interactive (defaults)
- Outputs
- AWS Integration
    - AWS prerequisites (IAM, DynamoDB, S3)
    - Run with AWS flags
    - What gets created
- Configuration
- Troubleshooting

---

## Overview

This repository provides a reproducible simulation to evaluate algorithmic strategies for distributing tasks across virtual machines (VMs). It produces metrics and publication-ready plots for side-by-side comparison.

## Features

- Three strategies: RR, RHO, ACO
- Metrics reporting and comparison plots
- Deterministic defaults with configurable parameters
- Optional AWS logging to DynamoDB and artifact upload to S3

## Project Structure

```
.
├── main.py                     # Main entry point
├── simulation.py               # Core experiment logic
├── entities.py                 # VM and Task definitions
├── config.py                   # Default simulation parameters
├── interactive.py              # Interactive user prompts
├── metrics.py                  # Metric calculation & printing
├── plotting.py                 # .png graph generation
├── aws_utils.py                # AWS DynamoDB & S3 integration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── algorithms/                 # Algorithm implementations
        ├── __init__.py
        ├── base.py
        ├── round_robin.py
        ├── rho.py
        └── aco.py
```

## Prerequisites

- Python 3.9+ (3.10 recommended)
- Optional (for cloud logging): AWS account and AWS CLI configured (`aws configure`)

## Quick Start

Create a virtual environment and install dependencies.

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux (bash):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run with default parameters (you’ll be prompted to keep defaults or customize):

```powershell
python main.py
```

Skip all prompts and use defaults:

```powershell
python main.py --skip-interactive
```

Run with custom parameters from the command line (no prompts):

```powershell
# Override a few parameters
python main.py --skip-interactive `
    --num-vms 16 `
    --vm-mips-range 200,1200 `
    --task-length-range 2000,40000 `
    --task-steps 200,400,800,1200 `
    --rho-weights 0.6,0.4 `
    --aco-params 1.0,2.0,0.1,0.1 `
    --random-seed 42
```

CLI flags:

- `--num-vms <int>`: number of VMs
- `--vm-mips-range min,max`: MIPS range for VMs
- `--task-length-range min,max`: task length (MI) range
- `--task-steps a,b,c`: list of task counts to simulate
- `--rho-weights w1,w2`: weights for time and energy (auto-normalized)
- `--aco-params alpha,beta,evap[,q0]`: ACO parameters; `q0` is greedy selection probability
- `--random-seed <int>`: set RNG seed for reproducible runs

Notes:

- The simulator uses SimPy for discrete-event processing with one FIFO queue per VM.
- Response time is measured at assignment time assuming tasks arrive at t=0; you can extend to non-zero arrivals easily within `simulation.py`.

### Outputs

The following plots are generated in the project directory after each run:

- `load_distribution.png`
- `metrics_comparison.png`
- `performance_graphs.png`

## AWS Integration

You can log every run to DynamoDB (metrics and metadata) and upload plots to S3 for archival/sharing.

### 1) AWS prerequisites

1. Create an IAM user with permissions (for prototyping only; scope down for production):
     - `AmazonDynamoDBFullAccess`
     - `AmazonS3FullAccess`
     - Configure credentials locally: `aws configure`

2. Create the DynamoDB table (PowerShell one-liner):

```powershell
aws dynamodb create-table --table-name LoadBalancingSimResults `
    --attribute-definitions AttributeName=RunID,AttributeType=S AttributeName=AlgorithmTaskCount,AttributeType=S `
    --key-schema AttributeName=RunID,KeyType=HASH AttributeName=AlgorithmTaskCount,KeyType=RANGE `
    --billing-mode PAY_PER_REQUEST
```

3. Create an S3 bucket (e.g., `my-load-balancing-graphs`) in your preferred region.

Default table name used by the app: `LoadBalancingSimResults`.

### 2) Run with AWS flags

```powershell
python main.py --skip-interactive `
    --aws-enabled `
    --s3-bucket my-load-balancing-graphs `
    --dynamo-table LoadBalancingSimResults
```

Flags:

- `--aws-enabled`  Enable AWS logging and uploads
- `--dynamo-table` DynamoDB table name (default: `LoadBalancingSimResults`)
- `--s3-bucket`    S3 bucket to receive `.png` plots
- `--aws-profile`  Optional AWS CLI profile to use

### 3) What gets created

- DynamoDB: Previous items are cleared, then metrics from the current run are inserted under a unique `RunID`.
- S3: All `.png` artifacts are uploaded to a prefix named with that `RunID` (e.g., `s3://my-load-balancing-graphs/sim-run-2025-11-07.../`).

## Configuration

- Edit defaults in `config.py` or use the interactive prompts in `main.py`.
- Algorithms are implemented under `algorithms/` (extend by adding new classes inheriting from `base.py`).

## Troubleshooting

- AWS credentials: run `aws sts get-caller-identity` to verify your setup.
- Region mismatches: ensure your S3 bucket and DynamoDB table are in the configured AWS region.
- Permissions: for production, replace the broad IAM policies with least-privilege, resource-scoped policies.

---

If you find this useful, consider starring the repo and opening issues/PRs for improvements.
