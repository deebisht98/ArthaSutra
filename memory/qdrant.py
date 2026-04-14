import asyncio
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from backend.app.config.settings import settings

# Initialize Async Qdrant Client
# Assuming QDRANT_URL is in the format "http://localhost:6333"
client = AsyncQdrantClient(url=settings.QDRANT_URL)

COLLECTION_NAME = "alpha_memory"
VECTOR_SIZE = 1536  # OpenAI embeddings size

async def init_collection():
    """Initializes the alpha_memory collection if it doesn't exist."""
    collections = await client.get_collections()
    collection_names = [c.name for c in collections.collections]

    if COLLECTION_NAME not in collection_names:
        print(f"Creating collection: {COLLECTION_NAME}")
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            ),
        )
        print(f"Collection {COLLECTION_NAME} created successfully.")
    else:
        print(f"Collection {COLLECTION_NAME} already exists.")

async def upsert_strategy(vector: List[float], payload: Dict[str, Any], point_id: Optional[str] = None):
    """
    Upserts a strategy vector and its metadata into Qdrant.
    """
    if point_id is None:
        point_id = str(uuid.uuid4())

    await client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
        ]
    )
    return point_id

async def search_strategies(query_vector: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Searches for strategies similar to the query vector.
    """
    search_result = await client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        with_vectors=False
    )

    return [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload
        }
        for hit in search_result.points
    ]

# Smoke test
if __name__ == "__main__":
    async def smoke_test():
        import numpy as np

        print("Starting Qdrant smoke test...")
        await init_collection()

        # Generate a dummy vector of 1536 dimensions
        dummy_vector = np.random.uniform(-1, 1, VECTOR_SIZE).tolist()
        dummy_payload = {"strategy_name": "SmokeTestStrategy", "version": "1.0"}

        print("Upserting dummy vector...")
        point_id = await upsert_strategy(dummy_vector, dummy_payload)
        print(f"Upserted point ID: {point_id}")

        print("Searching for similar vectors...")
        results = await search_strategies(dummy_vector, top_k=1)

        if results and results[0]["id"] == point_id:
            print("Smoke test PASSED: Successfully retrieved the inserted vector.")
            print(f"Match score: {results[0]['score']}")
        else:
            print("Smoke test FAILED: Could not retrieve the inserted vector or ID mismatch.")
            if results:
                print(f"Result ID: {results[0]['id']}, Expected: {point_id}")

    asyncio.run(smoke_test())
