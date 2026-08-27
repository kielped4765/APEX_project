from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Boolean, Text, create_engine)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import config

Base = declarative_base()           # Creates a base class factory using SQLAlchemy declarative system

class TelemetryRecord(Base):        # Defines a python class mapped to a database table named telemetry
    __tablename__ = 'telemetry'     # Defines the telemetry database table schema for storing each paramater for machine learning threat classifications
    id            = Column(Integer, primary_key=True, autoincrement=True)
    received_at   = Column(DateTime, default=datetime.utcnow, index=True)
    sequence_num  = Column(Integer, index=True)
    sim_time_s    = Column(Float)
    altitude_m    = Column(Float)
    airspeed_mps  = Column(Float)
    vertical_speed= Column(Float)
    pitch_rad     = Column(Float)
    roll_rad      = Column(Float)
    yaw_rad       = Column(Float)
    engine_rpm    = Column(Float)
    thrust_n      = Column(Float)
    fuel_flow_kgps= Column(Float)
    fuel_mass_kg  = Column(Float)
    g_load        = Column(Float)
    threat_class  = Column(Integer, default=0)
    ml_confidence = Column(Float, nullable=True)

class SecurityEvent(Base):          # This section defines the security_events table schema for logging security incidents and anomalies
    __tablename__ = 'security_events'
    id            = Column(Integer, primary_key=True, autoincrement=True)
    detected_at   = Column(DateTime, default=datetime.utcnow, index=True)
    sequence_num  = Column(Integer)
    threat_class  = Column(Integer)
    severity      = Column(String(16))
    description   = Column(Text)
    ml_confidence = Column(Float, nullable=True)
    acknowledged  = Column(Boolean, default=False)

_engine = None      # Initalizes a module-level global variable to hold the database engine singleton
def get_engine():   # Impliments a lazy-loading pattern for the database engine
    global _engine
    if _engine is None: 
        _engine = create_engine(config.DB_URL, echo=False)  # Automaticall runs Base.metadata.create_all(_engine) to generate the tables if they don't already exist.
        Base.metadata.create_all(_engine)
    return _engine
def get_session(): return sessionmaker(bind=get_engine())() # Factory function that returns a new database session bound to the engine.