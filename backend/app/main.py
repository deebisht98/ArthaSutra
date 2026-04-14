import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .config.settings import settings

# Ensure the repository root is on the import path for the memory package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from memory.mongo import mongodb_manager, check_mongo_health
from memory.qdrant import init_collection, upsert_strategy, search_strategies

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[{settings.ENVIRONMENT}] Application '{settings.PROJECT_NAME}' starting...")
    try:
        await mongodb_manager.connect()
        print("✓ MongoDB connection established")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        raise

    try:
        await init_collection()
        print("✓ Qdrant collection initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Qdrant collection: {e}")
        raise

    yield

    print(f"[{settings.ENVIRONMENT}] Application '{settings.PROJECT_NAME}' shutting down...")
    await mongodb_manager.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered trading system API",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }

@app.get("/test-mongo")
async def test_mongo():
    from memory.mongo import mongodb_manager

    log_id = await mongodb_manager.insert_backtest_log({
        "timestamp": "2026-04-13T18:58:00Z",
        "strategy": "test_strategy",
        "result": "success"
    })

    logs = await mongodb_manager.get_backtest_logs(limit=5)
    for log in logs:
        if "_id" in log:
            log["_id"] = str(log["_id"])

    return {
        "inserted_id": log_id,
        "logs": logs
    }

@app.get("/test-mongo-collections")
async def test_mongo_collections():
    collection_counts = {
        "backtest_logs": await mongodb_manager.backtest_logs.estimated_document_count(),
        "strategy_lineage": await mongodb_manager.strategy_lineage.estimated_document_count(),
        "portfolio_state": await mongodb_manager.portfolio_state.estimated_document_count(),
        "trade_logs": await mongodb_manager.trade_logs.estimated_document_count(),
        "quality_scores": await mongodb_manager.quality_scores.estimated_document_count(),
    }

    return {
        "mongo_status": "connected",
        "collection_counts": collection_counts
    }

@app.get("/test-qdrant")
async def test_qdrant():
    """Smoke test Qdrant vector operations."""
    import numpy as np

    # Generate a dummy vector of 1536 dimensions
    dummy_vector = np.random.uniform(-1, 1, 1536).tolist()
    dummy_payload = {"strategy_name": "SmokeTestStrategy", "version": "1.0"}

    # Upsert the vector
    point_id = await upsert_strategy(dummy_vector, dummy_payload)

    # Search for similar vectors
    results = await search_strategies(dummy_vector, top_k=1)

    return {
        "qdrant_status": "connected",
        "inserted_id": point_id,
        "search_results": results,
        "round_trip_success": bool(results and results[0]["id"] == point_id)
    }

@app.get("/health")
async def health_check():
    mongo_healthy = await check_mongo_health()
    if not mongo_healthy:
        raise HTTPException(status_code=503, detail="MongoDB connection unhealthy")

    return {
        "status": "healthy",
        "mongo_status": "healthy",
        "services": {
            "mongodb": "healthy"
        }
    }
