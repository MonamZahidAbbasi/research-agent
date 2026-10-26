from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str) -> list[str]:
    """Split the input text into chunks of specified size with overlap."""
    chunks=[]
    start=0
    text_length=len(text)
    while start<text_length:
        end=min(start+CHUNK_SIZE, text_length)
        chunk=text[start:end]
        chunks.append(chunk)
        if end==text_length:
            break
        start=start+CHUNK_SIZE-CHUNK_OVERLAP
    return chunks
        