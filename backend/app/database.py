import asyncpg
from .config import settings

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create database connection pool"""
        self.pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=1,
            max_size=10
        )
        print("✅ Database connected")
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            print("✅ Database disconnected")
    
    async def fetch_all(self, query: str, *args):
        """Fetch multiple rows"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetch_one(self, query: str, *args):
        """Fetch single row"""
        async with self.pool.acquire() as conn:
            if args:
                return await conn.fetchrow(query, *args)
            else:
                return await conn.fetchrow(query)
    
    async def execute(self, query: str, *args):
        """Execute query (insert, update, delete)"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

# Global database instance
db = Database()