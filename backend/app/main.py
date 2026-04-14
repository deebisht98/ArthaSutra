import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .core.config import settings

# Add root directory to path for importing memory module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from memory.mongo import mongodb_manager, check_mongo_health

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB on startup
    print(f"[{settings.ENVIRONMENT}] Application '{settings.PROJECT_NAME}' starting...")
    try:
        await mongodb_manager.connect()
        print("✓ MongoDB connection established")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        raise

    yield

    # Disconnect from MongoDB on shutdown
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
    """Test MongoDB async operations."""
    from memory.mongo import mongodb_manager

    # Insert a test log
    log_id = await mongodb_manager.insert_backtest_log({
        "timestamp": "2026-04-13T18:58:00Z",
        "strategy": "test_strategy",
        "result": "success"
    })

    # Retrieve logs
    logs = await mongodb_manager.get_backtest_logs(limit=5)

    # Convert ObjectIds to strings for JSON serialization
    for log in logs:
        if '_id' in log:
            log['_id'] = str(log['_id'])

    return {
        "inserted_id": log_id,
        "logs": logs
    }

@app.get("/test-mongo-collections")
async def test_mongo_collections():
    """Smoke test MongoDB collection handles and counts."""
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

@app.get("/health")
async def health_check():
    """Comprehensive health check including MongoDB."""
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
