import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, VectorParams, PointStruct, Filter,FieldCondition, MatchValue, FilterSelector, PayloadSchemaType)


from app.config import QDRANT_COLLECTION_NAME, EMBEDDING_DIMENSIONS
from app.rag.loaders import load_document
from app.rag.chunking import chunk_text
from app.rag.embedding import embed_chunks

load_dotenv()

qdrant_client=QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

def ensure_collection_exists():
    """Ensure that the Qdrant collection exists. If not, create it."""
    if not qdrant_client.collection_exists(QDRANT_COLLECTION_NAME):
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSIONS,
                distance=Distance.COSINE
            )
        )
        qdrant_client.create_payload_index(
            collection_name=QDRANT_COLLECTION_NAME,
            field_name="source",
            field_schema=PayloadSchemaType.KEYWORD,
        )

def ingest_file(file_path:str):
    ensure_collection_exists()
    source=os.path.basename(file_path)

    text=load_document(file_path)
    chunks=chunk_text(text)
    if not chunks:
        print(f"{source} text not found.")
        return 0
    vectors=embed_chunks(chunks)
    
    qdrant_client.delete(
        collection_name=QDRANT_COLLECTION_NAME,
        points_selector=FilterSelector(
            filter=Filter(must=[FieldCondition(key="source",match=MatchValue(value=source))])
        )
    )
    points=[
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source}:{i}")),
            vector=vector,
            payload={"text":chunk, "source":source,"chunk_index":i}
        )
        for i, (chunk,vector) in enumerate(zip(chunks,vectors))
    ]
    qdrant_client.upsert(collection_name=QDRANT_COLLECTION_NAME, points=points)
    print(f"{source}: {len(points)} point has been stored")
    return len(points)
    
        