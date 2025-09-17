def split_text(text, chunk_size=500, overlap=50):
    """
    Splits text into chunks of size `chunk_size` with overlap.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
