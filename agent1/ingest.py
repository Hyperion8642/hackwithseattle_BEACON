import os
import requests
import fitz  # PyMuPDF
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from agent1.config import QDRANT_URL, QDRANT_LOCAL_PATH, QDRANT_COLLECTION, EMBEDDING_MODEL

def get_qdrant_client():
    """Create Qdrant client: local file mode by default, server mode if QDRANT_URL is set."""
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL)
    return QdrantClient(path=QDRANT_LOCAL_PATH)

BOOK_URL = "https://kevin.wallace.seattle.wa.us/foi/thebook/The%20Book%20September%202020.pdf"
LOCAL_PDF_PATH = "the_book.pdf"

def download_book():
    if not os.path.exists(LOCAL_PDF_PATH):
        print("Downloading The Book...")
        # Since the actual link might be large or have SSL issues sometimes, we'll try to download it.
        # If it fails, we will fall back to a mock string.
        try:
            response = requests.get(BOOK_URL, verify=False, timeout=10)
            if response.status_code == 200:
                with open(LOCAL_PDF_PATH, 'wb') as f:
                    f.write(response.content)
                print("Download complete.")
            else:
                print("Failed to download, using mock data.")
                return False
        except Exception as e:
            print(f"Error downloading: {e}. Using mock data.")
            return False
    return True

def get_text_chunks():
    if download_book() and os.path.exists(LOCAL_PDF_PATH):
        try:
            doc = fitz.open(LOCAL_PDF_PATH)
            chunks = []
            for i, page in enumerate(doc):
                text = page.get_text()
                # Simple chunking: just split by paragraphs or 500 chars. Here we use pages for simplicity.
                if text.strip():
                    chunks.append({"text": text.strip()[:1000], "page": i + 1}) # Limit chunk size
                if i > 50: # Limit pages for demo
                    break
            if chunks:
                return chunks
        except Exception as e:
            print(f"Error reading PDF: {e}")

    # Mock data fallback
    return [
        {"text": "Code 200: Hazardous Coolant/Fluid Leak. If a coach is throwing green fluid or smells sweet, immediately report a Code 200.", "page": 10},
        {"text": "Medical Emergency: If a passenger collapses or is not moving, request EMS immediately and do not move the passenger.", "page": 12},
        {"text": "Collisions: Do not discuss liability or admit fault on scene. Distribute courtesy cards to all passengers. Preserve evidence.", "page": 15},
        {"text": "Security Threat: If a passenger produces a weapon, do not confront. Contact dispatch and request police.", "page": 18},
        {"text": "Mechanical failure: For general breakdowns not involving fluid, page a field supervisor.", "page": 20}
    ]

def main():
    print("Connecting to Qdrant...")
    client = get_qdrant_client()
    
    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Recreating collection...")
    if client.collection_exists(collection_name=QDRANT_COLLECTION):
        client.delete_collection(collection_name=QDRANT_COLLECTION)
        
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    )

    chunks = get_text_chunks()
    print(f"Embedding {len(chunks)} chunks...")
    
    # RocketRide requires a control document to validate the collection
    dim = model.get_sentence_embedding_dimension()
    schema_point = PointStruct(
        id=999999, # Arbitrary ID for schema
        vector=[0.0] * dim,
        payload={
            "objectId": "schema",
            "isDeleted": True,
            "metadata": {
                "vectorSize": dim,
                "modelName": EMBEDDING_MODEL
            }
        }
    )
    points = [schema_point]
    
    for i, chunk in enumerate(chunks):
        vector = model.encode(chunk["text"]).tolist()
        points.append(
            PointStruct(
                id=i,
                vector=vector,
                payload={
                    "objectId": f"doc_{i}",
                    "isDeleted": False,
                    "text": chunk["text"], 
                    "page": chunk["page"]
                }
            )
        )
    
    print("Upserting into Qdrant...")
    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points
    )
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
