import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
import re
from dotenv import load_dotenv
from models import Lead

load_dotenv()

async def get_leads():
    """Retrieve all leads from the database"""
    engine = create_async_engine(
        re.sub(r"^postgresql:", "postgresql+asyncpg:", os.getenv("DATABASE_URL") or ""),
        echo=True,
    )
    SessionLocal = async_sessionmaker(bind=engine)
    
    async with SessionLocal() as session:
        stmt = select(Lead)
        result = await session.execute(stmt)
        leads = result.scalars().all()
        
        print(f"Found {len(leads)} leads:")
        for lead in leads:
            print(f"  ID: {lead.post_id}")
            print(f"  Title: {lead.title}")
            print(f"  Description: {lead.post_text}")
            print(f"  URL: {lead.url}")
            print(f"  Subreddit: {lead.subreddit_name}")
            print("---")
        
        return leads

if __name__ == "__main__":
    asyncio.run(get_leads())