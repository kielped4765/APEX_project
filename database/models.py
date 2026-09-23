from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Boolean, Text, create_engine)
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from datetime import datetime
import config

Base = declarative_base()

class TelemetryRecord(Base):
    __tablename__ = 'telemetry'
    id              = Column(Integer, primary_key=True, autoincrement=True)
    received_at     = Column(DateTime, default=datetime.utcnow, index=True)
    sequence_num    = Column(Integer, index=True)
    sim_time_s      = Column(Float)
    altitude_m      = Column(Float)
    airspeed_mps    = Column(Float)
    vertical_speed  = Column(Float)
    pitch_rad       = Column(Float)
    roll_rad        = Column(Float)
    yaw_rad         = Column(Float)
    engine_rpm      = Column(Float)
    thrust_n        = Column(Float)
    fuel_flow_kgps  = Column(Float)
    fuel_mass_kg    = Column(Float)
    g_load          = Column(Float)
    threat_class    = Column(Integer, default=0)
    ml_confidence   = Column(Float, nullable=True)

class SecurityEvent(Base):
    __tablename__ = 'security_events'
    id              = Column(Integer, primary_key=True, autoincrement=True)
    detected_at     = Column(DateTime, default=datetime.utcnow, index=True)
    sequence_num    = Column(Integer)
    threat_class    = Column(Integer)
    severity        = Column(String(16))
    description     = Column(Text)
    ml_confidence   = Column(Float, nullable=True)
    acknowledged    = Column(Boolean, default=False)

_engine = None
def get_engine():
    global _engine
    if _engine is None: 
        _engine = create_engine(config.DB_URL, echo=False)
        Base.metadata.create_all(_engine)
    return _engine

_SessionLocal = None
def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal

@contextmanager
def get_session():
    """Context manager for CRUD background tasks: with get_session() as s:"""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db():
    """Standard generator function for FastAPI Depends(get_db)"""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
