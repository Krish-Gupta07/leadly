"""
Script to clear the Leadly database.
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, delete
import re

# Load environment variables
load_dotenv()

async def clear_database():
    """Clear all data from the Leadly database."""
    
    # Process the DATABASE_URL to handle sslmode parameter correctly
    database_url = os.getenv("DATABASE_URL") or ""
    # Replace postgresql: with postgresql+asyncpg:
    database_url = re.sub(r"^postgresql:", "postgresql+asyncpg:", database_url)
    # Remove sslmode parameter as it's not handled directly by asyncpg
    database_url = re.sub(r"\?sslmode=require$", "", database_url)
    database_url = re.sub(r"&sslmode=require", "", database_url)
    database_url = re.sub(r"\?sslmode=require&", "?", database_url)
    
    if not database_url:
        print("DATABASE_URL not found in environment variables")
        return
    
    # Create engine
    engine = create_async_engine(database_url, echo=True)
    SessionLocal = async_sessionmaker(bind=engine)
    
    try:
        async with SessionLocal() as session:
            # Import models
            from models import Lead, SubredditToScan, Comment
            
            # Delete all leads
            stmt = delete(Lead)
            result = await session.execute(stmt)
            print(f"Deleted {result.rowcount} leads")
            
            # Delete all comments
            stmt = delete(Comment)
            result = await session.execute(stmt)
            print(f"Deleted {result.rowcount} comments")
            
            # Delete all subreddit scans
            stmt = delete(SubredditToScan)
            result = await session.execute(stmt)
            print(f"Deleted {result.rowcount} subreddit entries")
            
            # Commit changes
            await session.commit()
            print("Database cleared successfully!")
            
    except Exception as e:
        print(f"Error clearing database: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(clear_database())