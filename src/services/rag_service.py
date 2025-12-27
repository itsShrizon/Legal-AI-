from sqlalchemy.orm import Session
from src.ml.rag_engine import LegalRAG
from src.ml.loader import ml_models
from src.core.config import settings
from qdrant_client import QdrantClient

# Global Qdrant Client (reused)
qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

def ask_question(db: Session, query: str):
    # Ensure models are loaded
    embedder = ml_models.get("embedding")
    llm = ml_models.get("llm")
    
    if not embedder or not llm:
        return "System is initializing models. Please try again in 5 seconds."
        
    rag = LegalRAG(db_session=db, qdrant_client=qdrant, embedder=embedder, llm=llm)
    return rag.search_and_answer(query)
