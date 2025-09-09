import os
import asyncio
import re
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Base, Lead, SubredditToScan
from typing import Optional

load_dotenv()


async def init_db():
    """Initialize the database and create tables if they don't exist"""
    # Process the DATABASE_URL to handle sslmode parameter correctly
    database_url = os.getenv("DATABASE_URL") or ""
    # Replace postgresql: with postgresql+asyncpg:
    database_url = re.sub(r"^postgresql:", "postgresql+asyncpg:", database_url)
    # Remove sslmode parameter as it's not handled directly by asyncpg
    database_url = re.sub(r"\?sslmode=require$", "", database_url)
    database_url = re.sub(r"&sslmode=require", "", database_url)
    database_url = re.sub(r"\?sslmode=require&", "?", database_url)

    engine = create_async_engine(
        database_url,
        echo=True,
    )
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    return engine


async def save_leads(url_description_map: dict, subreddit_names: Optional[list] = None, category: str = "neutral"):
    """
    Save leads to the database

    Args:
        url_description_map (dict): Dictionary with identifiers as keys and descriptions as values
        subreddit_names (list): List of subreddit names the leads came from
        category (str): Category of the leads (hot, cold, neutral)
    """
    engine = await init_db()
    SessionLocal = async_sessionmaker(bind=engine)

    async with SessionLocal() as session:
        for identifier, description in url_description_map.items():
            # Extract ID from identifier
            # No prefixing needed anymore as we're using actual Reddit IDs
            subreddit_name = "unknown"
            
            # If we couldn't extract subreddit from URL, use the provided subreddit names
            if subreddit_name == "unknown" and subreddit_names:
                if isinstance(subreddit_names, list):
                    subreddit_name = subreddit_names[0] if subreddit_names else "unknown"
                elif isinstance(subreddit_names, str):
                    subreddit_name = subreddit_names

            # Extract URL from description if it's included
            url = f"https://www.reddit.com/comments/{identifier}"  # Default URL
            if "\n\nURL: " in description:
                # Extract the URL from the description
                parts = description.split("\n\nURL: ")
                actual_description = parts[0]
                url = parts[1] if len(parts) > 1 else url
            else:
                actual_description = description

            # Check if lead already exists
            stmt = select(Lead).where(Lead.post_id == identifier)
            result = await session.execute(stmt)
            existing_lead = result.scalar_one_or_none()

            if not existing_lead:
                # Create new lead
                lead = Lead(
                    post_id=identifier,
                    title=f"Lead from {identifier}",
                    post_text=actual_description,
                    url=url,
                    subreddit_name=subreddit_name,
                    category=category,  # Add category
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
