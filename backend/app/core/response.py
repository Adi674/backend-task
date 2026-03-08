from typing import Any, Optional
from fastapi.responses import JSONResponse

def success_response(
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200
):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": message,
            "data": data
        }
    )

def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[Any] = None
):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "errors": errors
        }
    )