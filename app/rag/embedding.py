import os
from dotenv import load_dotenv
from app.config import EMBEDDING_MODEL,EMBEDDING_DIMENSIONS,EMBEDDING_BATCH_SIZE
from google import genai
from google.genai import types

load_dotenv()
gemini_client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def embed_query(query:str)->list[float]:
    """Generate an embedding for the given query using the Gemini Embedding model."""
    result=gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS)
    )
    return result.embeddings[0].values

def embed_chunks(chunks:list[str]):
    """Generate embeddings for a list of text chunks using the Gemini Embedding model."""
    all_vectors=[]
    for i in range(0, len(chunks),EMBEDDING_BATCH_SIZE):
        batch=chunks[i:i+EMBEDDING_BATCH_SIZE]
        results=gemini_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS)
        )
        all_vectors.extend([embedding.values for embedding in results.embeddings])
    return all_vectors
