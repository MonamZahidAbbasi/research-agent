import os 
import sys

sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.ingestion import ingest_file, qdrant_client
from app.config import QDRANT_COLLECTION_NAME

DOCS_DIR="knowledge_docs"
for name in os.listdir(DOCS_DIR):
    if name.lower().endswith((".pdf",".txt")):
        ingest_file(os.path.join(DOCS_DIR,name))
print("collection count:",qdrant_client.count(QDRANT_COLLECTION_NAME).count)