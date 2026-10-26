import os
import sys
from app.config import QDRANT_COLLECTION_NAME
from app.rag.ingestion import qdrant_client
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if qdrant_client.collection_exists(QDRANT_COLLECTION_NAME):
    qdrant_client.delete_collection(QDRANT_COLLECTION_NAME)
    print("Collection deleted")
else:
    print("collection doesnot exists")