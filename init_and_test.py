import time
import random
from sqlalchemy.orm import sessionmaker
from database.models import engine, Base, TelemetryRecord

# Ensure tables are created
Base.metadata.create_all(bind=engine)
print("Database and telemetry table initialized successfully!")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

for i in range(2, 200):
    record = TelemetryRecord(
        timestamp=str(float(i)),
        altitude_m=3000.0 + random.randint(-50, 50),
        airspeed_mps=120.5 + random.random() * 5,
        vertical_speed=1.2,
        pitch_rad=0.05,
        roll_rad=0.0,
        engine_rpm=5000.0,
        thrust_n=30000.0,
        fuel_flow_kgps=0.6,
        g_load=1.0,
        attack_label="CLEAN"
    )
    db.add(record)
    db.commit()
    print(f"Inserted live telemetry row {i}")
    time.sleep(1)

db.close()
