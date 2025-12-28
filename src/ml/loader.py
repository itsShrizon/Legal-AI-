from src.core.config import settings
from src.ml.embeddings import BanglaEmbedding

class ModelLoader:
    @staticmethod
    def load_embedding_model():
        print(f"Loading Embedding Model from {settings.EMBEDDING_MODEL_PATH}...")
        return BanglaEmbedding(model_path=settings.EMBEDDING_MODEL_PATH)

    @staticmethod
    def load_llm_model():
        from src.ml.llm import BanglaLLM
        return BanglaLLM()

# Global dictionary to hold loaded models
ml_models = {}
