from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "errors": None
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(e) for e in error["loc"]),
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation failed",
            "errors": errors
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "errors": str(exc)
        }
    )