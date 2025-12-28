import json
import os
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.data.models import LegalDocument, LegalChunk
from src.ml.loader import ml_models
from src.core.config import settings

# Global Qdrant Client
qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
COLLECTION_NAME = "bangla_legal"

class IngestionService:
    @staticmethod
    def setup_qdrant():
        collections = qdrant.get_collections()
        if COLLECTION_NAME not in [c.name for c in collections.collections]:
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )

    @staticmethod
    def process_and_ingest(db: Session, file_path: str):
        IngestionService.setup_qdrant()
        embedder = ml_models.get("embedding") # Getting model from singleton
        
        if not embedder:
            # Fallback for when running script directly without main.py lifespan
            from src.ml.embeddings import BanglaEmbedding
            embedder = BanglaEmbedding(model_path=settings.EMBEDDING_MODEL_PATH)

        points = []
        
        from tqdm import tqdm
        
        # Count lines for progress bar (rough estimate or precise depending on needs, simple loop first)
        num_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        print(f"Detected {num_lines} chunks to ingest.")

        with open(file_path, "r", encoding="utf-8") as f:
            for line in tqdm(f, total=num_lines, desc="Ingesting Chunks"):
                data = json.loads(line)
                
                # A. Check/Create Document in SQL
                filename = data['metadata']['source_file']
                doc = db.query(LegalDocument).filter_by(filename=filename).first()
                if not doc:
                    doc = LegalDocument(filename=filename, title=filename.replace(".txt", ""))
                    db.add(doc)
                    db.commit()
                    db.refresh(doc)
                
                # B. Store Chunk in SQL
                # Check if chunk exists first
                existing_chunk = db.query(LegalChunk).filter_by(chunk_id=data['chunk_id']).first()
                if not existing_chunk:
                    chunk = LegalChunk(
                        chunk_id=data['chunk_id'],
                        document_id=doc.id,
                        content=data['text'],
                        hierarchy=data['metadata']['hierarchy'],
                        token_count=data['token_count']
                    )
                    db.add(chunk)
                
                # C. Generate Vector
                vector = embedder.encode(data['text'])
                
                points.append(models.PointStruct(
                    id=abs(hash(data['chunk_id'])) % ((2**64) - 1), 
                    vector=vector,
                    payload={
                        "chunk_id": data['chunk_id'],
                        "hierarchy": data['metadata']['hierarchy'], 
                        "source_file": filename,
                        "text": data['text'] 
                    }
                ))
                
                # Batch Insert Logic
                if len(points) >= 100:
                    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
                    points = [] # Reset batch

        # Insert remaining points
        if points:
            qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
        
        db.commit()
        return num_lines
