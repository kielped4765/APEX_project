import sqlite3
import time
import random
from datetime import datetime

conn = sqlite3.connect('telemetry.db')
cursor = conn.cursor()

# Create table matching the SQLAlchemy model schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        received_at DATETIME,
        sequence_num INTEGER,
        sim_time_s REAL,
        altitude_m REAL,
        airspeed_mps REAL,
        vertical_speed REAL,
        pitch_rad REAL,
        roll_rad REAL,
        yaw_rad REAL,
        engine_rpm REAL,
        thrust_n REAL,
        fuel_flow_kgps REAL,
        fuel_mass_kg REAL,
        g_load REAL,
        threat_class INTEGER DEFAULT 0,
        ml_confidence REAL
    )
''')
conn.commit()
print("Telemetry table verified/created successfully with correct schema!")

for i in range(2, 200):
    cursor.execute('''
        INSERT INTO telemetry (
            received_at, sequence_num, sim_time_s, altitude_m, airspeed_mps, 
            vertical_speed, pitch_rad, roll_rad, yaw_rad, engine_rpm, 
            thrust_n, fuel_flow_kgps, fuel_mass_kg, g_load, threat_class, ml_confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.utcnow(), i, float(i), 
        3000.0 + random.randint(-50, 50), 120.5 + random.random() * 5, 1.2, 
        0.05, 0.0, 0.0, 5000.0, 30000.0, 0.6, 500.0, 1.0, 0, 0.05
    ))
    conn.commit()
    print(f"Inserted live telemetry row {i}")
    time.sleep(1)

conn.close()