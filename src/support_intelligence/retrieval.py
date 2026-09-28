import os
from functools import lru_cache
from uuid import uuid4

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

COLLECTION = "support_documents_semantic"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
VECTOR_SIZE = 384

client = QdrantClient(url=os.getenv("QDRANT_URL", "http://127.0.0.1:6333"))


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    """Load the embedding model once per API process."""
    return TextEmbedding(model_name=MODEL_NAME)


def embed_text(text: str) -> list[float]:
    """Convert text into a semantic vector."""
    vector = next(get_embedding_model().embed([text]))
    return vector.tolist()


def ensure_collection() -> None:
    """Create the semantic collection when it does not exist."""
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )


def add_document(text: str, source: str) -> str:
    """Embed and store a support document with its source."""
    ensure_collection()
    document_id = str(uuid4())

    client.upsert(
        collection_name=COLLECTION,
        points=[
            models.PointStruct(
                id=document_id,
                vector=embed_text(text),
                payload={"text": text, "source": source},
            )
        ],
    )
    return document_id


def search_documents(query: str, limit: int = 3) -> list[dict]:
    """Find documents whose meaning is close to the query."""
    ensure_collection()
    result = client.query_points(
        collection_name=COLLECTION,
        query=embed_text(query),
        limit=limit,
        with_payload=True,
    )

    return [
        {
            "id": str(point.id),
            "score": point.score,
            "text": point.payload["text"],
            "source": point.payload["source"],
        }
        for point in result.points
    ]