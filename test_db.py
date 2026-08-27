import os
import config
from database.models import get_engine, get_session, TelemetryRecord, SecurityEvent
from database.crud import (
    write_telemetry, 
    write_security_event, 
    get_recent_telemetry, 
    get_security_events, 
    get_summary_stats
)

def run_tests():
    print("--- [1/5] Initializing Database Engine ---")
    engine = get_engine()
    print(f"Database URL active: {config.DB_URL}")
    
    # Ensure the local data directory exists if using a local sqlite file path
    db_path = config.DB_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created missing directory: {db_dir}")

    print("\n--- [2/5] Testing Telemetry Write Operation ---")
    mock_state = {
        'sequence_num': 1,
        'sim_time_s': 0.02,
        'altitude_m': 3000.0,
        'airspeed_mps': 120.5,
        'vertical_speed': 1.2,
        'pitch_rad': 0.05,
        'roll_rad': 0.0,
        'yaw_rad': 0.0,
        'engine_rpm': 5000.0,
        'thrust_n': 30000.0,
        'fuel_flow_kgps': 0.6,
        'fuel_mass_kg': 2000.0,
        'g_load': 1.0
    }
    write_telemetry(mock_state, threat_class=0, ml_confidence=None)
    print("Successfully wrote mock telemetry record.")

    print("\n--- [3/5] Testing Security Event Write Operation ---")
    write_security_event(
        seq=1,
        tc=3,
        sev="HIGH",
        desc="Test unit test verification failure (Corrupted payload)",
        conf=0.92
    )
    print("Successfully wrote mock security event.")

    print("\n--- [4/5] Testing Read & Query Helpers ---")
    recent_telem = get_recent_telemetry(limit=5)
    print(f"Fetched {len(recent_telem)} telemetry row(s). Latest sequence: {recent_telem[-1]['sequence_num']}")

    events = get_security_events(limit=5)
    print(f"Fetched {len(events)} security event(s). Latest severity: {events[0]['severity']}")

    stats = get_summary_stats()
    print(f"Summary Statistics Report: {stats}")

    print("\n--- [5/5] Test Suite Completed Successfully! ---")
    print("All models and CRUD handlers are functioning properly without errors.")

if __name__ == "__main__":
    run_tests()