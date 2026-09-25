# APEX: Flight Telemetry & Real-Time Threat Detection Pipeline

## 🚀 What is APEX?
APEX is an end-to-end, high-performance telemetry and security monitoring pipeline designed for aerospace simulations. It bridges a simulated flight engine with a modern web-based monitoring dashboard, featuring real-time data streaming, database persistence, and machine learning-driven threat classification.

---

## 🏗️ System Architecture
The pipeline relies on three core concurrent layers:
1. **Simulation Engine (`sim_test_pure.py`)**: Generates aircraft flight dynamics (altitude, airspeed, G-load, etc.) and streams them directly into a centralized SQLite database (`telemetry.db`).
2. **FastAPI Backend (`api/main.py`)**: Acts as the HTTP bridge, querying the database and serving optimized JSON telemetry endpoints.
3. **Streamlit Dashboard (`dashboard/app.py`)**: A reactive frontend client that auto-refreshes every second to render live metrics, trend graphs, and machine learning threat predictions.

---

## 🛠️ Running the Project From Scratch

To run the complete pipeline locally from scratch, open **3 separate terminal tabs** and execute the setup and service commands below.

### Initial Setup (Run in any terminal first)
Ensure your virtual environment is active, dependencies are installed, and the database schema is clean:
```bash
cd /mnt/c/Users/peder/APEX_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Reset the database to ensure a clean schema slate

## Step-by-Step Service Startup (3 Terminals Required)

## Terminal 1: Simulation Engine (Data Producer)

cd /mnt/c/Users/peder/APEX_project
source .venv/bin/activate
python sim_test_pure.py

## Terminal 2: FastAPI Backend

cd /mnt/c/Users/peder/APEX_project
source .venv/bin/activate
DATABASE_URL="sqlite:///./telemetry.db" uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

## Terminal 3: Streamlit Dashboard

cd /mnt/c/Users/peder/APEX_project
source .venv/bin/activate
streamlit run dashboard/app.py