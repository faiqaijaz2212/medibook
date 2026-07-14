from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app import models  # Import models to ensure they are registered on Base.metadata
from app.routers import (
    health,
    auth,
    users,
    departments,
    doctors,
    patients,
    appointments,
    medical_records,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all database tables
    Base.metadata.create_all(bind=engine)

    yield

    # Place shutdown tasks here later if needed


app = FastAPI(
    title="MediBook API",
    lifespan=lifespan,
)

# Configure CORS Middleware
origins = [
    "http://localhost:3000",  # React / NextJS default dev port
    "http://localhost:5173",  # Vite default dev port
    "http://localhost:8501",  # Streamlit default dev port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(medical_records.router)