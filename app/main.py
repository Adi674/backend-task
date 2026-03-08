from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware   # ← move to top
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from app.core.config import settings
import app.db.registry
from app.db.base import Base
from app.db.session import engine
from app.api.v1 import auth, tasks
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="Scalable REST API with Auth & Role-Based Access",
    version="1.0.0"
)

# ✅ CORS first — before everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ OPTIONS preflight handler
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
        }
    )

# Error handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])

@app.get("/")
def root():
    return {"status": "success", "message": "Task Manager API is running 🚀"}