from fastapi import APIRouter, Depends, HTTPException       # APIRouter to split routes across multiple files, Depends for dependancy injection, and HTTPException for handling errors
from sqlalchemy.orm import Session                          # Imports SQLAlchemy Session type hint to manage database transactions safely inside path operations.
from database.models import get_session, TelemetryRecord, SecurityEvent     # Imports the database session generator function alongside the ORM data models representing the telemetry and security tables.
from pydantic import BaseModel   # Imports Pydantics BaseModel to handle data validation, serialization, and documentation
from typing import List      

router = APIRouter(prefix="/api", tags=["APEX API"])    # Initalizes the router object with a common /api path prefix and tags it for clean grouping

class TelemetryResponse(BaseModel):     # Defines a Pydantic schema dictating the structure of telemetry data returned to clients
    id: int
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float

    class Config:                       # Within the Pydantic schema, this config class is used to configure behavior for the model.
        orm_mode = True

@router.get("/telemetry/live", response_model=List[TelemetryResponse])  # Registers a GET endpoint at /api/telemetry/live thatyields a list of schema objects
def get_live_telemetry(limit: int = 50, session: Session = Depends(get_session)):   # Defines the endpoint controller. It accepts an optional limit query parameter and injects an active database session using FastAPI's dependency injection.
    records = session.query(TelemetryRecord).order_by(TelemetryRecord.id.desc()).limit(limit).all() # Queries the database, sorting records by descending ID
    return records

@router.get("/health")      # Creates a simple hearbeat endpoint to confirm the service is up and running.
def health_check():
    return {"status": "healthy", "system": "APEX Telemetry Active"}