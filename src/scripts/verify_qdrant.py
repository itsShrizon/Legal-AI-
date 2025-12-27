import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.config import settings
from qdrant_client import QdrantClient

def verify_connection():
    print(f"Connecting to Qdrant at: {settings.QDRANT_URL}")
    if settings.QDRANT_API_KEY:
        print("Using API Key authentication")
    else:
        print("No API Key provided (Anonymous/Local mode)")

    try:
        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        collections = client.get_collections()
        print(f"✅ Connected! Found {len(collections.collections)} collections.")
        for col in collections.collections:
            print(f" - {col.name}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    verify_connection()
