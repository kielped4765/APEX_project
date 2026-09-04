"""
Real time APEX Telemetry & Threat Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import joblib
from collections import daque
from receiver import listen_unix, parse_frame
from verifier import FrameVerifier
import config

# Defines the page title and layout and sets main header text
st.set_page_config(page_title = "APEX Security Dashboard", layout="wide")   
st.title("APEX Flight Telemetry & Threat Dashboard")

# Caches the machine learning model and scaler loading function so they only load once
@st.cache_resource
def load_ml():  # defines the function that loads and returns the classifier and scaler files
    return joblib.load('ml/classifier.pkl'), joblib.load('ml/scaler.pkl')   

clf, scaler = load_ml() # executes the cached loader to fetch the model and scaler objects
FEATURES = ['altitude_m','airspeed_mps','vertical_speed','pitch_rad','roll_rad',
    'engine_rpm','thrust_n','fuel_flow_kgps','g_load',
    'thrust_speed_ratio','climb_thrust_ratio','seq_delta','fuel_per_thrust']
CLASSES = ['CLEAN','SPOOF','REPLAY','CORRUPT','DRIFT']  # defines the threat class category labels

max_len = 50    # sets the maximum number of history records to retain in the rolling window
history = deque([{k: 0.0 for k in FEATURES}, {'label': 'CLEAN'}], maxlen=max_len)   # initalizes the rolling history deque

placeholder = st.empty()    # creates a dynamic container placeholder to refresh UI components
vfy = FrameVerifier(config.get_aes_key(), config.get_hmac_key())    # instantiates the frame verifier using AES and HMAC keys
prev_seq = 0

for raw in listen_unix(config.SOCKET_PATH): # loops continuously over incoming raw frames from UNIX socket
    frame = parse_frame(raw)
    if not frame: continue
    act_label = frame.attack_label
    _, state = vfy.verify(frame)

    if state is None:
        feats = [0.0]*len(FEATURES)
        pred_label = "Corrupt"

    else:
        sd = state['sequence_num'] - prev_seq
        feats = [
            state['altitude_m'], state['airspeed_mps'], state['vertical_speed'],
            state['pitch_rad'], state['roll_rad'], state['engine_rpm'],
            state['thrust_n'], state['fuel_flow_kgps'], state['g_load'],
            state['thrust_n']/(state['airspeed_mps']+1e-3),
            state['vertical_speed']/(state['thrust_n']+1e-3),
            float(sd), state['fuel_flow_kgps']/(state['thrust_n']+1e-3)
        ]
        prev_seq = int(state['sequence_num'])   # updates the previous sequence tracker
        scaled = scaler.transform([feats])      # standardizes the feature vector using the filtered scaler
        pred_idx = clf.predict(scaled)[0]       # performs ML inference to predict the threat class index
        pred_label = CLASSES[pred_idx]

    history.append({**dict(zip(FEATURES, feats)), 'label': pred_label,
                    'actual': act_label})   # appends the latest telemetry data point and predictions 
    df = pd.DataFrame(history)

    with placeholder.container():   # Updates the UI container in place during each iteration of the loop
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Altitude", f"{df['altitude_m'].iloc[-1]:.1f} m")
        m2.metric("Airspeed", f"{df['airspeed_mps'].iloc[-1]:.1f} m/s")
        m3.metric("Predicted Threat", pred_label, 
                  delta="ALERT" if pred_label != "CLEAN" else "Normal",
                  delta_color="inverse" if pred_label != "CLEAN" else "normal")
        m4.metric("Actual Label", act_label)

        st.subheader("Live Telemetry Trends")
        st.line_chart(df[['altitude_m', 'airspeed_mps']])

        st.subheader("Recent Frame Log Histroy")
        st.dataframe(df[['altitude_m', 'airspeed_mps', 'label', 'actual']].tail(5), use_container_width=True)