"""
MongoDB async connection setup using Motor.

This module provides asynchronous MongoDB operations for the ArthaSutra trading system.
Handles connections to MongoDB, database operations, and collection management.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional, Dict, Any, List
import logging
import sys
import os

# Add the parent directory to path so package imports like app.core.config work reliably.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDBManager:
    """Manages MongoDB connections and operations asynchronously."""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._collections: Dict[str, AsyncIOMotorCollection] = {}

    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            # Test the connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")

            # Create database reference
            self.database = self.client.artha_sutra

            # Initialize collections
            self._init_collections()

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"MongoDB connection failed: {e}")

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    def _init_collections(self) -> None:
        """Initialize collection references."""
        collections = {
            'backtest_logs': 'backtest_logs',
            'strategy_lineage': 'strategy_lineage',
            'portfolio_state': 'portfolio_state',
            'trade_logs': 'trade_logs',
            'quality_scores': 'quality_scores'
        }

        for name, collection_name in collections.items():
            self._collections[name] = self.database[collection_name]

    async def health_check(self) -> bool:
        """Check if MongoDB connection is healthy."""
        try:
            if not self.client:
                return False
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False

    # Collection accessors
    @property
    def backtest_logs(self) -> AsyncIOMotorCollection:
        """Access to backtest_logs collection."""
        return self._collections['backtest_logs']

    @property
    def strategy_lineage(self) -> AsyncIOMotorCollection:
        """Access to strategy_lineage collection."""
        return self._collections['strategy_lineage']

    @property
    def portfolio_state(self) -> AsyncIOMotorCollection:
        """Access to portfolio_state collection."""
        return self._collections['portfolio_state']

    @property
    def trade_logs(self) -> AsyncIOMotorCollection:
        """Access to trade_logs collection."""
        return self._collections['trade_logs']

    @property
    def quality_scores(self) -> AsyncIOMotorCollection:
        """Access to quality_scores collection."""
        return self._collections['quality_scores']

    # Helper methods for common operations
    async def insert_backtest_log(self, log_data: Dict[str, Any]) -> str:
        """Insert a backtest log entry."""
        result = await self.backtest_logs.insert_one(log_data)
        return str(result.inserted_id)

    async def get_backtest_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent backtest logs."""
        cursor = self.backtest_logs.find().sort('timestamp', -1).limit(limit)
        return await cursor.to_list(length=None)

    async def update_portfolio_state(self, portfolio_id: str, state: Dict[str, Any]) -> bool:
        """Update portfolio state."""
        result = await self.portfolio_state.update_one(
            {'portfolio_id': portfolio_id},
            {'$set': state},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None

    async def get_portfolio_state(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve portfolio state."""
        return await self.portfolio_state.find_one({'portfolio_id': portfolio_id})

# Global MongoDB manager instance
mongodb_manager = MongoDBManager()

# Convenience functions for direct access
async def get_mongo_client() -> AsyncIOMotorClient:
    """Get the MongoDB client."""
    return mongodb_manager.client

async def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance."""
    return mongodb_manager.database

async def check_mongo_health() -> bool:
    """Check MongoDB connection health."""
    return await mongodb_manager.health_check()
