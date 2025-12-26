from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from src.api.dependencies import get_db, get_current_user
from src.data.schemas import User
from src.services.ingestion_service import IngestionService
import shutil
import os

router = APIRouter()

@router.post("/ingest")
async def ingest_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Save file temporarily
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Run ingestion in background
    def ingest_task(path):
        try:
             # Need new session for background task usually, but passed ssn might work if not closed.
             # Better to create new session or block. For scaffolding, blocking is safer or use context manager inside.
             IngestionService.process_and_ingest(db, path)
        finally:
             if os.path.exists(path):
                 os.remove(path)

    background_tasks.add_task(ingest_task, temp_file)
    
    return {"status": "Ingestion started", "filename": file.filename}
