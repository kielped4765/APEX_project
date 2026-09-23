import sqlite3
import time
import random

conn = sqlite3.connect('telemetry.db')
cursor = conn.cursor()

# Create table if it doesn't exist yet
cursor.execute('''
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        altitude_m REAL,
        airspeed_mps REAL,
        vertical_speed REAL,
        pitch_rad REAL,
        roll_rad REAL,
        engine_rpm REAL,
        thrust_n REAL,
        fuel_flow_kgps REAL,
        g_load REAL,
        attack_label TEXT
    )
''')
conn.commit()
print("Telemetry table verified/created successfully!")

for i in range(2, 200):
    cursor.execute('''
        INSERT INTO telemetry (timestamp, altitude_m, airspeed_mps, vertical_speed, pitch_rad, roll_rad, engine_rpm, thrust_n, fuel_flow_kgps, g_load, attack_label)
        VALUES (?, ?, ?, ?, 0.05, 0.0, 5000.0, 30000.0, 0.6, 1.0, 'CLEAN')
    ''', (str(float(i)), 3000.0 + random.randint(-50, 50), 120.5 + random.random() * 5, 1.2))
    conn.commit()
    print(f"Inserted live telemetry row {i}")
    time.sleep(1)

conn.close()
