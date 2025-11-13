# Cloud Load Balancing Simulation (RR • RHO • ACO)

Simulate and compare three load-balancing algorithms—Round Robin (RR), Rock Hyrax Optimization (RHO), and Ant Colony Optimization (ACO)—in a heterogeneous cloud environment. Run locally or on a cloud VM (e.g., AWS EC2), and optionally log results to AWS DynamoDB.

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
    - AWS prerequisites (IAM, DynamoDB)
    - Run with AWS flags
    - What gets created
    - Plot from DynamoDB logs
    - CloudWatch metrics & dashboard
- Configuration
- Troubleshooting

---

## Overview

This repository provides a reproducible simulation to evaluate algorithmic strategies for distributing tasks across virtual machines (VMs). It produces metrics and publication-ready plots for side-by-side comparison.

## Features

- Three strategies: RR, RHO, ACO
- Metrics reporting and comparison plots
- Deterministic defaults with configurable parameters
- Optional AWS logging to DynamoDB

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
├── aws_utils.py                # AWS DynamoDB integration
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

You can log every run to DynamoDB (metrics and metadata). Plots are saved locally on the machine where the simulation runs; you can also regenerate them from DynamoDB.

### 1) AWS prerequisites

1. Create an IAM user/role with permissions (for prototyping only; scope down for production):
    - `AmazonDynamoDBFullAccess`
    - Configure credentials locally: `aws configure`

2. DynamoDB table creation is automatic

If the table does not exist, the app will create it for you with the required keys:
`RunID` (partition key, String) and `AlgorithmTaskCount` (sort key, String). Default table name: `LoadBalancingSimResults`.

### 2) Run with AWS flags

```powershell
python main.py --aws-enabled --dynamo-table LoadBalancingSimResults
```

Flags:

- `--aws-enabled`  Enable AWS logging to DynamoDB
- `--dynamo-table` DynamoDB table name (default: `LoadBalancingSimResults`)
- `--aws-profile`  Optional AWS CLI profile to use

### 3) What gets created

- DynamoDB: Previous items are cleared, then metrics from the current run are inserted under a unique `RunID`. Final per-VM finish times and assignment logs are also stored to enable full plot regeneration later.

### 4) Plot from DynamoDB logs

You can regenerate the performance graph directly from DynamoDB (useful on a fresh machine or after the local artifacts are gone):

```powershell
python aws_plot.py --run-id <YOUR_RUN_ID> `
    --dynamo-table LoadBalancingSimResults `
    --aws-profile <optional_profile>
```

This will produce `performance_graphs.png` in the project directory using the metrics stored in DynamoDB. With the latest code, per-VM finish times and assignment logs are also stored in DynamoDB, so the bar charts (`load_distribution.png` and `metrics_comparison.png`) will be regenerated as well.

### CloudWatch metrics & dashboard

When `--aws-enabled` is used, the run also publishes custom CloudWatch metrics and creates a run-specific dashboard comparing algorithms:

- Namespace: `LoadBalancerMetrics`
- Dimensions: `Algorithm`, `RunID`
- Metrics: `AverageResponseTime` (s), `Makespan` (s), `Throughput` (tasks/sec), `TotalEnergy` (kJ), and an aggregate `PerformanceScore` (0–100)

The dashboard is named `Load_Balancer_Comparison_<RunID>` and contains bar charts to compare algorithms side-by-side. You can find it in the CloudWatch console under Dashboards (ensure you’re in the same AWS region as your credentials).

## Configuration

- Interactive prompts are the default; you can still override any specific setting via CLI flags.
- Edit defaults in `config.py` or use the interactive prompts in `main.py`.
- Algorithms are implemented under `algorithms/` (extend by adding new classes inheriting from `base.py`).

## Troubleshooting

- AWS credentials: run `aws sts get-caller-identity` to verify your setup.
- Region mismatches: ensure your DynamoDB table is in the configured AWS region.
- Permissions: for production, replace the broad IAM policies with least-privilege, resource-scoped policies.

---

If you find this useful, consider starring the repo and opening issues/PRs for improvements.
