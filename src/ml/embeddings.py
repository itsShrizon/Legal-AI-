import pickle
import torch
import os
import io

class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        return super().find_class(module, name)

class BanglaEmbedding:
    def __init__(self, model_path="models/embedding_model.pkl"):
        print(f"Loading Fine-Tuned Bangla Embeddings from {model_path}...")
        
        if not os.path.exists(model_path):
            print(f"WARNING: Model file {model_path} not found. Using placeholder.")
            self.model = None
            return

        try:
            print("Attempting to load with custom CPU_Unpickler...")
            with open(model_path, 'rb') as f:
                self.model = CPU_Unpickler(f).load()
        except Exception as e:
            print(f"Custom unpickler failed: {e}")
            print("Falling back to standard torch.load...")
            # Fallback (though likely to fail if the above failed)
            self.model = torch.load(model_path, map_location='cpu', weights_only=False)
            
    def encode(self, text: str):
        if self.model is None:
            # Return dummy vector for testing
            return [0.0] * 384 
            
        with torch.no_grad():
            return self.model.encode(text).tolist()
