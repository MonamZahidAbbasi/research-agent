import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from app.config import QDRANT_COLLECTION_NAME, TOP_K_RESULTS, SCORE_THRESHOLD
from app.rag.embedding import embed_query

load_dotenv()
qdrant_client=QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

def search_qdrant(query:str, top_k:int=TOP_K_RESULTS)->list[dict]:
    """Search Qdrant for relevant documents based on the query.
    Returns a list of documents with their content and metadata.
    """
    try:
        if not qdrant_client.collection_exists(collection_name=QDRANT_COLLECTION_NAME):
            print(f"Collection '{QDRANT_COLLECTION_NAME}' does not exist.")
            return []
        query_vector=embed_query(query)
        results=qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=top_k
        )
        return[
            {
                "title":point.payload.get("source","internal document"),
                "url":"",
                "content":point.payload.get("text",""),
                "score":point.score
            }
            for point in results.points
            if point.score>=SCORE_THRESHOLD
        ]
    except Exception as e:
        print(f"Error during Qdrant search: {e}")
        return []
