"""
Real-time APEX Telemetry & Threat Dashboard (FastAPI Client)
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import joblib
from streamlit_autorefresh import st_autorefresh

# Defines the page title and layout
st.set_page_config(page_title="APEX Security Dashboard", layout="wide")
st.title("APEX Flight Telemetry & Threat Dashboard")

count = st_autorefresh(interval=1000, limit=None, key="telemetry_counter")

# Caches the machine learning model loading function
@st.cache_resource
def load_ml():
    return joblib.load('ml/classifier.pkl'), joblib.load('ml/scaler.pkl')

try:
    clf, scaler = load_ml()
except Exception:
    clf, scaler = None, None

FEATURES = [
    'altitude_m', 'airspeed_mps', 'vertical_speed', 'pitch_rad', 'roll_rad',
    'engine_rpm', 'thrust_n', 'fuel_flow_kgps', 'g_load',
    'thrust_speed_ratio', 'climb_thrust_ratio', 'seq_delta', 'fuel_per_thrust'
]

API_URL = "http://127.0.0.1:8000/api/telemetry/live?limit=50"

# Fetch latest telemetry data from FastAPI backend
try:
    response = requests.get(API_URL, timeout=2)
    records = response.json() if response.status_code == 200 else []
except Exception as e:
    st.error(f"Connection Error: {e}")
    records = []

if records:
    current_history = []
    for r in reversed(records):
        feats = [
            r.get('altitude_m', 0.0), 
            r.get('airspeed_mps', 0.0), 
            r.get('vertical_speed', 0.0),
            r.get('pitch_rad', 0.0), 
            r.get('roll_rad', 0.0), 
            r.get('engine_rpm', 0.0),
            r.get('thrust_n', 0.0), 
            r.get('fuel_flow_kgps', 0.0), 
            r.get('g_load', 1.0),
            r.get('thrust_n', 0.0) / (r.get('airspeed_mps', 0.0) + 1e-3),
            r.get('vertical_speed', 0.0) / (r.get('thrust_n', 0.0) + 1e-3),
            1.0,
            r.get('fuel_flow_kgps', 0.0) / (r.get('thrust_n', 0.0) + 1e-3)
        ]
        pred_label = r.get('attack_label', 'CLEAN')
        act_label = r.get('attack_label', 'CLEAN')
        current_history.append({**dict(zip(FEATURES, feats)), 'label': pred_label, 'actual': act_label})
    
    # If we only have 1 record, duplicate it so charts and frames render without bounds errors
    if len(current_history) == 1:
        current_history.append(current_history[0].copy())

    df = pd.DataFrame(current_history)

    pred_label = df['label'].iloc[-1]
    act_label = df['actual'].iloc[-1]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Altitude", f"{df['altitude_m'].iloc[-1]:.1f} m")
    m2.metric("Airspeed", f"{df['airspeed_mps'].iloc[-1]:.1f} m/s")
    m3.metric("Predicted Threat", pred_label, 
              delta="ALERT" if pred_label != "CLEAN" else "Normal",
              delta_color="inverse" if pred_label != "CLEAN" else "normal")
    m4.metric("Actual Label", act_label)

    st.subheader("Live Telemetry Trends")
    st.line_chart(df[['altitude_m', 'airspeed_mps']])

    st.subheader("Recent Frame Log History")
    st.dataframe(df[['altitude_m', 'airspeed_mps', 'label', 'actual']].tail(5), width='stretch')
else:
    st.warning("Waiting for telemetry data from FastAPI backend...")

# streamlit-autorefresh handles the trigger automatically based on interval=1000