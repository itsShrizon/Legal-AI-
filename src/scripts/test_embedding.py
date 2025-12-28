import sys
import os
import time

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.config import settings
from src.ml.loader import ModelLoader

def test_embedding_model():
    print(f"Testing Embedding Model loading from: {settings.EMBEDDING_MODEL_PATH}")
    
    start_time = time.time()
    try:
        model = ModelLoader.load_embedding_model()
        print(f" Model loaded successfully in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f" Failed to load model: {e}")
        return

    text = "বাংলাদেশের সংবিধান"
    print(f"Testing encoding for text: '{text}'")
    
    try:
        vector = model.encode(text)
        print(f" Vector generation successful.")
        print(f"Vector length: {len(vector)}")
        print(f"First 5 dimensions: {vector[:5]}")
        
        if len(vector) == 384:
            print(" Dimensions match expected (384)")
        else:
            print(f" Unexpected dimension: {len(vector)}")
            
    except Exception as e:
        print(f" Encoding failed: {e}")

if __name__ == "__main__":
    test_embedding_model()
