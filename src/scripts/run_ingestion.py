import sys
import os
import asyncio
sys.path.append(os.getcwd())

from src.services.ingestion_service import IngestionService
from src.ml.loader import ModelLoader

async def main():
    # Models are handled within IngestionService if not found in global ml_models
    
    file_path = "data/raw/chunked_legal_documents_smart.jsonl"
    print(f"Ingesting {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist.")
        return

    # Simulate file upload handler - we don't have a DB session easily here without mocking
    # Ideally, we should use the API endpoint, but using the service function directly is fine 
    # if we mock the db session or create a real one.
    
    # Actually, ingest_file requires a db session. 
    from src.data.db import SessionLocal
    db = SessionLocal()
    
    try:
        # IngestionService.process_and_ingest is synchronous, so no await
        result = IngestionService.process_and_ingest(db=db, file_path=file_path)
        print("Ingestion Result (Chunks processed):", result)
    except Exception as e:
        print(f"Ingestion failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
