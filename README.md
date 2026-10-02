# APEX is a real-time telemetry and data-driven monitoring platform. It is architected around three concurrent services designed to simulate data generation, process it through a secure backend API, and visualize it dynamically via an interactive dashboard:

## Simulation Engine (sim_test_pure.py): Acts as the data producer, simulating live telemetry metrics and writing them to the database.

## FastAPI Backend (api/main.py): A robust, modular REST API built with FastAPI and SQLAlchemy that manages database sessions, endpoints, and data routing.

## Streamlit Dashboard (dashboard/app.py): A modern web interface utilizing live auto-refreshing components to display system health, security metrics, and real-time telemetry.

## Prerequisites & System Environment
This project runs natively on Linux (WSL) to prevent cross-platform file format and virtual environment discrepancies. Ensure you have Python 3.10+ and python3-venv installed.

### Initial Setup (Run Once)
Open your terminal inside your project root directory (/mnt/c/Users/peder/APEX_project) and run the following commands to initialize your native Linux virtual environment and install all required dependencies:

Bash
# 1. Create a native Linux virtual environment
python3 -m venv .venv

# 2. Upgrade pip inside the virtual environment
./.venv/bin/python -m pip install --upgrade pip

# 3. Install project dependencies
./.venv/bin/python -m pip install -r requirements.txt
Running the Application (3 Terminals Required)
To run the complete system stack locally, you will need 3 separate terminal panes open in VS Code, all pointed at your project root directory.

Terminal 1: Simulation Engine (Data Producer)
Activate your virtual environment and launch the simulation script:

# Bash
source .venv/bin/activate
python sim_test_pure.py
Terminal 2: FastAPI Backend
Activate your virtual environment and start the uvicorn server with the appropriate SQLite database configuration:

# Bash
source .venv/bin/activate
DATABASE_URL="sqlite:///./telemetry.db" ./.venv/bin/uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
Terminal 3: Streamlit Dashboard
Activate your virtual environment and launch the live-monitoring web interface:

# Bash
source .venv/bin/activate
streamlit run dashboard/app.py
Once all three services are running, open your browser and navigate to http://localhost:8501 to interact with the dashboard.