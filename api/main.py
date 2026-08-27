from fastapi import FastAPI     # Imports core FastAPI class, which is used to instantiate the web application and manage routes, middleware and application lifecycle events.
from fastapi.middleware.cors import CORSMiddleware  # Import cross-orgin resource sharing (CORS) middleware. 
from api.routes import router                       # Imports the modular API router from api/routes.py which groups all the specific telemetry, security, and health-check endpoints
from database.models import get_engine              # Imports the database engine initialization function from the SQLAlchemy ORM setup

app = FastAPI(title='APEX Telemetry API', version='1.0.0')  # Initalizes the Fast application instance with custom metadata
app.add_middleware(CORSMiddleware, allow_origins=['*'],     # Registers the CORS middleware and setting the allow_origins permits requests from any origin, preventing the browser's same origin policy from blocking communications.
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.on_event('startup')    # A FastAPI event decorator that registers the decorated asynchronous function to run automatically right when the server boots up.
async def startup():        # Defines the asynchronous startup hook function.
    get_engine() # creates tables on first run

app.include_router(router)
# Run: uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
# Docs: http://localhost:8000/docs