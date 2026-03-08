from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
import os
from app.core.config import settings
# Import registry FIRST — registers all models with Base
import app.db.registry

from app.db.base import Base
from app.db.session import engine
from app.api.v1 import auth, tasks
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="Scalable REST API with Auth & Role-Based Access",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

# ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global error handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Task Manager API is running 🚀"
    }
