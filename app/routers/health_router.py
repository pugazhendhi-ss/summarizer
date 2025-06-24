from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import logging

health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    """To check the API server running status"""
    try:
        return JSONResponse(
            content={
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "API server is up and healthy"
            },
            status_code=200
        )
    except Exception as e:
        logging.exception("Health check failed")
        return JSONResponse(
            content={
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": str(e)
            },
            status_code=500
        )
