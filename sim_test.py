import sqlite3, time, random

conn = sqlite3.connect('telemetry.db')
cursor = conn.cursor()

for i in range(2, 200):
    cursor.execute('''
        INSERT INTO telemetry (timestamp, altitude_m, airspeed_mps, vertical_speed, pitch_rad, roll_rad, engine_rpm, thrust_n, fuel_flow_kgps, g_load, attack_label)
        VALUES (?, ?, ?, ?, 0.05, 0.0, 5000.0, 30000.0, 0.6, 1.0, 'CLEAN')
    ''', (str(float(i)), 3000.0 + random.randint(-50, 50), 120.5 + random.random()*5, 1.2))
    conn.commit()
    print(f"Inserted row {i}")
    time.sleep(1)

conn.close()
