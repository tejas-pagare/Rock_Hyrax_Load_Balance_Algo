# Rock Hyrax Load Balancing Algorithm: Setup and Deployment Guide

This guide provides step-by-step instructions for setting up the project, running simulations, and deploying the environment to AWS.

## 1. Project Overview

This project simulates and compares different load balancing algorithms for cloud computing environments. It allows for the analysis of performance metrics like makespan and energy consumption.

**Implemented Algorithms:**
- Round Robin
- Ant Colony Optimization (ACO)
- Rock Hyrax Optimization (RHO)

## 2. Local Setup and Execution

Follow these steps to run the simulation on your local machine.

### Step 1: Clone the Repository
First, get the project code onto your machine.

```bash
git clone <repository-url>
cd Rock_Hyrax_Load_Balance_Algo
```

### Step 2: Create a Python Virtual Environment
Isolate the project's dependencies from your system's Python installation.

```bash
# Create the virtual environment
python -m venv venv

# Activate it (command differs for Windows vs. macOS/Linux)
# Windows (Command Prompt or PowerShell):
venv\Scripts\activate
# macOS/Linux (bash):
source venv/bin/activate
```
Your terminal prompt should now be prefixed with `(venv)`.

### Step 3: Install Required Libraries
Install the Python libraries needed to run the simulation.

```bash
pip install -r requirements.txt
```

### Step 4: Run the Simulation
You can run the simulation in two modes:

**A) Default Mode (Recommended)**
This runs the simulation with the default parameters defined in `config.py`.

```bash
python test_runner.py
```

**B) Interactive Mode**
This mode will prompt you to enter custom parameters for the simulation.

```bash
python interactive.py
```

### Step 5: View the Results
After the simulation completes, the following files will be generated in the project's root directory:
- `load_distribution.png`: A chart showing how tasks were assigned to each VM.
- `metrics_comparison.png`: Bar charts comparing the performance of each algorithm.
- `performance_graphs.png`: Line graphs showing how algorithms perform as the workload increases.

Simply open these image files to view the results.

---

## 3. AWS EC2 Deployment Guide

This section explains how to run the simulation on a virtual server (EC2 instance) on AWS.

### Step 1: Launch an AWS EC2 Instance
1.  Navigate to the **EC2 Dashboard** in your AWS Console.
2.  Click **"Launch Instances"**.
3.  **Name:** Give your instance a name (e.g., `LoadBalanceSim`).
4.  **Application and OS Images (AMI):** Select **Ubuntu**, and choose an image like `Ubuntu Server 22.04 LTS`.
5.  **Instance type:** Select `t2.micro` (this is eligible for the AWS Free Tier).
6.  **Key pair (login):**
    - Create a new key pair.
    - **Key pair name:** `ec2-key`
    - **Key pair type:** RSA, `.pem` format.
    - Click **"Create key pair"** and **download the `.pem` file**. Store it in a secure and memorable location.
7.  **Network settings:**
    - Click **"Edit"**.
    - Under **"Firewall (security groups)"**, find the inbound rule for SSH.
    - Change the **"Source type"** to **"My IP"** to ensure only you can connect to the instance.
8.  Click **"Launch instance"**.

### Step 2: Connect to Your EC2 Instance
1.  Go back to the EC2 Instances list and select your newly created instance.
2.  Find the **"Public IPv4 address"** in the details panel.
3.  Open a terminal on your local machine, navigate to where you saved your `.pem` file, and run the following commands.

```bash
# Restrict permissions for your key file (required for SSH)
# Replace 'ec2-key.pem' with the actual name of your key file.
chmod 400 ec2-key.pem

# Connect to the instance via SSH
# Replace 'your-instance-ip' with the Public IPv4 address from the console.
ssh -i "ec2-key.pem" ubuntu@your-instance-ip
```
If successful, you will be logged into your Ubuntu server on AWS.

### Step 3: Set Up the Environment on EC2
Now, inside the SSH session, run these commands to prepare the server.

```bash
# Update the server's package manager
sudo apt update

# Install Python, pip, and Git
sudo apt install -y python3 python3-pip git

# Clone the project repository from your Git provider
git clone <your-repository-url>
cd Rock_Hyrax_Load_Balance_Algo

# Install the Python dependencies
pip3 install -r requirements.txt
```

### Step 4: Run the Simulation on EC2
With the setup complete, run the simulation just as you did locally.

```bash
python3 test_runner.py
```
The script will execute, and the output images will be saved inside the `Rock_Hyrax_Load_Balance_Algo` directory on the EC2 instance.

### Step 5: Retrieve Results from EC2
To view the generated images, you need to copy them from the EC2 instance to your local machine. **Open a new local terminal** (do not close your SSH connection yet) and use the `scp` command.

```bash
# Navigate to the directory where your .pem key is stored locally.
# This command copies all .png files from the EC2 instance to your current local directory.
# Replace 'your-instance-ip' with your instance's IP.
scp -i "ec2-key.pem" ubuntu@your-instance-ip:~/Rock_Hyrax_Load_Balance_Algo/*.png .
```
The `.png` files will now be on your local machine for you to view.

### Step 6: Terminate the EC2 Instance (Important!)
To avoid incurring unexpected charges, **terminate** the EC2 instance once you are finished.
1.  Go to the EC2 Instances page in the AWS Console.
2.  Select the instance.
3.  Click **"Instance state"** -> **"Terminate instance"**.