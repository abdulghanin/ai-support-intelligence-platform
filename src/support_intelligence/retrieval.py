import hashlib
import math
import os
from uuid import uuid4

from qdrant_client import QdrantClient, models

COLLECTION = "support_documents"
VECTOR_SIZE = 256

client = QdrantClient(url=os.getenv("QDRANT_URL", "http://127.0.0.1:6333"))


def vectorize(text: str) -> list[float]:
    normalized = " ".join(text.lower().split())
    values = [0.0] * VECTOR_SIZE

    for index in range(max(0, len(normalized) - 2)):
        part = normalized[index:index + 3]
        digest = hashlib.blake2b(part.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest, "big") % VECTOR_SIZE
        values[bucket] += 1.0

    length = math.sqrt(sum(value * value for value in values))
    if length:
        return [value / length for value in values]
    return values


def ensure_collection() -> None:
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )


def add_document(text: str, source: str) -> str:
    ensure_collection()
    document_id = str(uuid4())
    client.upsert(
        collection_name=COLLECTION,
        points=[
            models.PointStruct(
                id=document_id,
                vector=vectorize(text),
                payload={"text": text, "source": source},
            )
        ],
    )
    return document_id


def search_documents(query: str, limit: int = 3) -> list[dict]:
    ensure_collection()
    result = client.query_points(
        collection_name=COLLECTION,
        query=vectorize(query),
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