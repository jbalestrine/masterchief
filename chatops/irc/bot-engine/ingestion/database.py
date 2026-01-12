"""Database ingestion for IRC bot."""
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from enum import Enum

from .base import BaseIngestion, IngestionEvent, IngestionStatus

logger = logging.getLogger(__name__)


class DBType(Enum):
    """Database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


class DatabaseIngestion(BaseIngestion):
    """Database polling ingestion."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize database ingestion.
        
        Config options:
            - db_type: Database type (postgresql, mysql, sqlite, mongodb)
            - connection_string: Database connection string
            - query: SQL query or MongoDB query
            - polling_interval: Seconds between polls (default: 60)
            - change_detection: Track changes (default: True)
            - key_field: Field to use for change detection
        """
        super().__init__(source_id, config)
        self.db_type = DBType(config.get('db_type'))
        self.connection_string = config.get('connection_string')
        self.query = config.get('query')
        self.polling_interval = config.get('polling_interval', 60)
        self.change_detection = config.get('change_detection', True)
        self.key_field = config.get('key_field', 'id')
        self.last_keys = set()
        self._task = None
        self._connection = None
    
    async def _connect(self):
        """Connect to database."""
        try:
            if self.db_type == DBType.POSTGRESQL:
                await self._connect_postgresql()
            elif self.db_type == DBType.MYSQL:
                await self._connect_mysql()
            elif self.db_type == DBType.SQLITE:
                await self._connect_sqlite()
            elif self.db_type == DBType.MONGODB:
                await self._connect_mongodb()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def _connect_postgresql(self):
        """Connect to PostgreSQL."""
        try:
            import asyncpg
            self._connection = await asyncpg.connect(self.connection_string)
            logger.info("Connected to PostgreSQL")
        except ImportError:
            logger.error("asyncpg not installed. Install with: pip install asyncpg")
            raise
    
    async def _connect_mysql(self):
        """Connect to MySQL."""
        try:
            import aiomysql
            # Parse connection string
            # Format: mysql://user:pass@host:port/db
            import re
            match = re.match(r'mysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', self.connection_string)
            if match:
                user, password, host, port, db = match.groups()
                self._connection = await aiomysql.connect(
                    host=host,
                    port=int(port),
                    user=user,
                    password=password,
                    db=db
                )
                logger.info("Connected to MySQL")
        except ImportError:
            logger.error("aiomysql not installed. Install with: pip install aiomysql")
            raise
    
    async def _connect_sqlite(self):
        """Connect to SQLite."""
        try:
            import aiosqlite
            # Extract path from connection string
            path = self.connection_string.replace('sqlite://', '')
            self._connection = await aiosqlite.connect(path)
            logger.info("Connected to SQLite")
        except ImportError:
            logger.error("aiosqlite not installed. Install with: pip install aiosqlite")
            raise
    
    async def _connect_mongodb(self):
        """Connect to MongoDB."""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self._connection = AsyncIOMotorClient(self.connection_string)
            logger.info("Connected to MongoDB")
        except ImportError:
            logger.error("motor not installed. Install with: pip install motor")
            raise
    
    async def _query_data(self) -> List[Dict[str, Any]]:
        """Execute query and return results."""
        try:
            if self.db_type == DBType.POSTGRESQL:
                return await self._query_postgresql()
            elif self.db_type == DBType.MYSQL:
                return await self._query_mysql()
            elif self.db_type == DBType.SQLITE:
                return await self._query_sqlite()
            elif self.db_type == DBType.MONGODB:
                return await self._query_mongodb()
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    async def _query_postgresql(self) -> List[Dict[str, Any]]:
        """Query PostgreSQL."""
        rows = await self._connection.fetch(self.query)
        return [dict(row) for row in rows]
    
    async def _query_mysql(self) -> List[Dict[str, Any]]:
        """Query MySQL."""
        async with self._connection.cursor() as cursor:
            await cursor.execute(self.query)
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def _query_sqlite(self) -> List[Dict[str, Any]]:
        """Query SQLite."""
        async with self._connection.execute(self.query) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def _query_mongodb(self) -> List[Dict[str, Any]]:
        """Query MongoDB."""
        import json
        # Parse query (expected to be JSON string)
        query = json.loads(self.query)
        
        # Extract collection and query
        collection_name = query.get('collection')
        find_query = query.get('query', {})
        
        db = self._connection[query.get('database', 'test')]
        collection = db[collection_name]
        
        cursor = collection.find(find_query)
        results = []
        async for doc in cursor:
            # Convert ObjectId to string
            doc['_id'] = str(doc['_id'])
            results.append(doc)
        
        return results
    
    async def _poll_loop(self):
        """Main polling loop."""
        while self.status == IngestionStatus.RUNNING:
            try:
                results = await self._query_data()
                
                if results:
                    # Change detection
                    if self.change_detection:
                        current_keys = {row.get(self.key_field) for row in results}
                        new_keys = current_keys - self.last_keys
                        
                        if new_keys:
                            new_rows = [row for row in results if row.get(self.key_field) in new_keys]
                            
                            event = IngestionEvent(
                                source_type="db",
                                source_id=self.source_id,
                                data={'rows': new_rows, 'count': len(new_rows)},
                                metadata={
                                    'db_type': self.db_type.value,
                                    'query': self.query,
                                    'new_count': len(new_keys),
                                    'total_count': len(results)
                                },
                                timestamp=time.time()
                            )
                            
                            await self._dispatch_event(event)
                        
                        self.last_keys = current_keys
                    else:
                        # No change detection, emit all results
                        event = IngestionEvent(
                            source_type="db",
                            source_id=self.source_id,
                            data={'rows': results, 'count': len(results)},
                            metadata={
                                'db_type': self.db_type.value,
                                'query': self.query
                            },
                            timestamp=time.time()
                        )
                        
                        await self._dispatch_event(event)
                
                await asyncio.sleep(self.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
                await asyncio.sleep(self.polling_interval)
    
    async def start(self):
        """Start database polling."""
        self.status = IngestionStatus.STARTING
        try:
            await self._connect()
            self.status = IngestionStatus.RUNNING
            self._task = asyncio.create_task(self._poll_loop())
            logger.info(f"Database polling started")
        except Exception as e:
            self.status = IngestionStatus.ERROR
            logger.error(f"Failed to start database polling: {e}")
            raise
    
    async def stop(self):
        """Stop database polling."""
        self.status = IngestionStatus.STOPPED
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        # Close connection
        if self._connection:
            if self.db_type == DBType.POSTGRESQL:
                await self._connection.close()
            elif self.db_type == DBType.MYSQL:
                self._connection.close()
            elif self.db_type == DBType.SQLITE:
                await self._connection.close()
            elif self.db_type == DBType.MONGODB:
                self._connection.close()
        
        logger.info(f"Database polling stopped")
