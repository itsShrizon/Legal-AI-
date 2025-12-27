from fastapi import APIRouter
from src.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}
