# ☁️ Cloud Load Balancing Simulation (RR, RHO, ACO)

This project simulates and compares three cloud load balancing algorithms —
Round Robin (RR), Rock Hyrax Optimization (RHO), and Ant Colony Optimization (ACO) —
within a heterogeneous cloud environment.

It supports both local and cloud-based execution (e.g., on AWS EC2), and includes integrated AWS logging:

* **DynamoDB** → Stores simulation metrics
* **S3** → Uploads generated performance and load distribution graphs

---

## 🧠 Features

* Simulation of three advanced load balancing algorithms (RR, RHO, ACO)
* Comparison of algorithm performance using visual metrics and graphs
* Dynamic VM and task generation for heterogeneous cloud environments
* AWS integration for real-time storage and analysis
* Command-line options for flexible execution (interactive or automated)

---

## 📁 Project Structure

```bash
.
├── main.py                # Main entry point
├── simulation.py          # Core experiment logic
├── entities.py            # VM and Task definitions
├── config.py              # Default simulation parameters
├── interactive.py         # Interactive user prompt handler
├── metrics.py             # Metric calculation & result printing
├── plotting.py            # Graph generation (.png)
├── aws_utils.py           # AWS DynamoDB & S3 integration
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── algorithms/            # Algorithm implementations
    ├── base.py
    ├── round_robin.py
    ├── rho.py
    └── aco.py

⚙️ Local Execution
1. Setup
Clone the repository:
 git clone [https://github.com/tejas-pagare/Rock_Hyrax_Load_Balance_Algo.git](https://github.com/tejas-pagare/Rock_Hyrax_Load_Balance_Algo.git)
 cd Rock_Hyrax_Load_Balance_Algo

Create and activate a virtual environment:
 python -m venv venv
 source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
 pip install -r requirements.txt

2. Run the Simulation
Run with default parameters:
 python main.py

