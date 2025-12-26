import pickle
import torch
import os

class BanglaEmbedding:
    def __init__(self, model_path="models/embedding_model.pkl"):
        print(f"Loading Fine-Tuned Bangla Embeddings from {model_path}...")
        
        # Check if file exists to avoid crash during scaffolding
        if not os.path.exists(model_path):
            print(f"WARNING: Model file {model_path} not found. Using placeholder.")
            self.model = None
            return

        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
            
    def encode(self, text: str):
        if self.model is None:
            # Return dummy vector for testing
            return [0.0] * 384 
            
        with torch.no_grad():
            return self.model.encode(text).tolist()
