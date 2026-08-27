# CRUD (Create, Read, Update, Delete) File

from database.models import get_session, TelemetryRecord, SecurityEvent

def write_telemetry(state: dict, threat_class: int, ml_confidence) -> None:     # Defines a function that takes in threat classification, state disctionary, and an ML confidence score
    """Writes an incoming telemetry state record into the database"""
    with get_session() as s:     # Opens a database session using a Python context manager which automatically closes or rolls back if an error occurs.
        s.add(TelemetryRecord(   # Maps individual dictionary keys from the state payload (such as airspeed, engine stats, altitude etc) into a new TelemetryRecord instance
            sequence_num=int(state['sequence_num']),
            sim_time_s=state['sim_time_s'],
            altitude_m=state['altitude_m'],   
            airspeed_mps=state['airspeed_mps'],
            vertical_speed=state['vertical_speed'], 
            pitch_rad=state['pitch_rad'],
            roll_rad=state['roll_rad'],        
            yaw_rad=state['yaw_rad'],
            engine_rpm=state['engine_rpm'],    
            thrust_n=state['thrust_n'],
            fuel_flow_kgps=state['fuel_flow_kgps'], 
            fuel_mass_kg=state['fuel_mass_kg'],
            g_load=state['g_load'], 
            threat_class=threat_class,
            ml_confidence=ml_confidence
        ))
        s.commit()          # Permanently writes (commits) the staged record to the SQLite database.

def write_security_event(seq: int, tc: int, sev: str, desc: str, conf) -> None:     # Defines a helper function to record security anomalies or attacks.
    """Records a secuity anomly or threat event into the database."""
    with get_session() as s:        # Opens a safe context-managed databse session
        s.add(SecurityEvent(
        sequence_num=seq, 
            threat_class=tc,
            severity=sev, 
            description=desc, 
            ml_confidence=conf    
        ))
        s.commit()

def get_recent_telemetry(limit: int = 120) -> list:     # Fetches a limited number of the most recent telemetry rows
    """Retrives the most recent telemetry records ordered chronologically."""
    with get_session() as s:
        rows = (s.query(TelemetryRecord)
                .order_by(TelemetryRecord.received_at.desc())
                .limit(limit).all())
        return [_to_dict(r) for r in reversed(rows)]

def get_security_events(severity: str = None, limit: int = 50) -> list:     # Queries logged security events ordered by detection time.
    """Retrives logged security events, optionally filtered by severity level."""
    with get_session() as s:
        q = s.query(SecurityEvent).order_by(SecurityEvent.detected_at.desc())
        if severity:
            q = q.filter(SecurityEvent.severity == severity)
        return [_to_dict(r) for r in q.limit(limit).all()]

def get_summary_stats() -> dict:        # Executes lightweight SQL aggregate count queries to calculate total frames.
    """Computes high-level aggregate counts for frames, threats, and alerts."""
    with get_session() as s:
        return {
            'total_frames': s.query(TelemetryRecord).count(),
            'total_threats': s.query(SecurityEvent).count(),
            'critical': s.query(SecurityEvent).filter(
                SecurityEvent.severity == 'CRITICAL').count(),
            'unacknowledged': s.query(SecurityEvent).filter(
                SecurityEvent.acknowledged == False).count()
        }

def _to_dict(row) -> dict:      # Uses SQLAlchemy table introspection to dynamically convert a database model instance into a standard python dictionary.
    """Helper utility to convert SQLAlchemy model rows into JSON-compatible dictionaries."""
    d = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    for k, v in d.items():
        if hasattr(v, 'isoformat'):
            d[k] = v.isoformat()
    return d