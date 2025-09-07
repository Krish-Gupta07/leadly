import os
import asyncio
import re
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Base, Lead, SubredditToScan

load_dotenv()


async def init_db():
    """Initialize the database and create tables if they don't exist"""
    engine = create_async_engine(
        re.sub(r"^postgresql:", "postgresql+asyncpg:", os.getenv("DATABASE_URL") or ""),
        echo=True,
    )
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    return engine


async def save_leads(url_description_map: dict):
    """
    Save leads to the database

    Args:
        url_description_map (dict): Dictionary with URLs as keys and descriptions as values
    """
    engine = await init_db()
    SessionLocal = async_sessionmaker(bind=engine)

    async with SessionLocal() as session:
        for url, description in url_description_map.items():
            # Extract ID from URL (assuming format https://reddit.com/comments/{id})
            post_id = url.split("/")[-1] if "/" in url else url

            # Check if lead already exists
            stmt = select(Lead).where(Lead.post_id == post_id)
            result = await session.execute(stmt)
            existing_lead = result.scalar_one_or_none()

            if not existing_lead:
                # Create new lead
                lead = Lead(
                    post_id=post_id,
                    title=f"Lead from {post_id}",
                    post_text=description,
                    url=url,
                    subreddit_name="unknown",  # We don't have this info in the current data structure
                )
                session.add(lead)

        await session.commit()


async def get_scanned_subreddits():
    """
    Get all active subreddits that should be scanned

    Returns:
        list: List of subreddit names
    """
    engine = await init_db()
    SessionLocal = async_sessionmaker(bind=engine)

    try:
        async with SessionLocal() as session:
            stmt = select(SubredditToScan.name).where(SubredditToScan.is_active == True)
            result = await session.execute(stmt)
            return [row[0] for row in result.fetchall()]
    except Exception as e:
        print(f"Error getting scanned subreddits: {e}")
        return []  # Return empty list as fallback


async def save_scanned_subreddit(subreddit_name: str):
    """
    Save a subreddit to the database as scanned

    Args:
        subreddit_name (str): Name of the subreddit
    """
    engine = await init_db()
    SessionLocal = async_sessionmaker(bind=engine)

    try:
        async with SessionLocal() as session:
            # Use INSERT ... ON CONFLICT to avoid duplicates
            stmt = insert(SubredditToScan).values(name=subreddit_name, is_active=True)
            stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
            await session.execute(stmt)
            await session.commit()
    except Exception as e:
        print(f"Error saving scanned subreddit {subreddit_name}: {e}")


async def get_leads(limit: int = 100, offset: int = 0):
    """
    Get leads from the database

    Args:
        limit (int): Maximum number of leads to return
        offset (int): Number of leads to skip

    Returns:
        list: List of leads
    """
    engine = await init_db()
    SessionLocal = async_sessionmaker(bind=engine)

    try:
        async with SessionLocal() as session:
            stmt = select(Lead).offset(offset).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()
    except Exception as e:
        print(f"Error getting leads: {e}")
        return []


# For testing purposes
if __name__ == "__main__":
    asyncio.run(init_db())
