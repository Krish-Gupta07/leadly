import asyncio
from reddit_data_extractor import get_reddit_data
from leadFinderAi import find_leads
from url_mapper import process_ai_output
from db import save_leads, get_scanned_subreddits, save_scanned_subreddit
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
import re
from dotenv import load_dotenv
from job_tracker import JobStatus
from job_tracker import get_job

load_dotenv()


class LeadlyController:
    def __init__(self):
        # Process the DATABASE_URL to handle sslmode parameter correctly
        database_url = os.getenv("DATABASE_URL") or ""
        # Replace postgresql: with postgresql+asyncpg:
        database_url = re.sub(r"^postgresql:", "postgresql+asyncpg:", database_url)
        # Remove sslmode parameter as it's not handled directly by asyncpg
        database_url = re.sub(r"\?sslmode=require$", "", database_url)
        database_url = re.sub(r"&sslmode=require", "", database_url)
        database_url = re.sub(r"\?sslmode=require&", "?", database_url)

        self.engine = create_async_engine(
            database_url,
            echo=True,
        )
        self.SessionLocal = async_sessionmaker(bind=self.engine)

    async def run_lead_finder(self, user_query: str, subreddits=None, job_id=None):
        """
        Central controller method that orchestrates the entire lead finding process

        Args:
            user_query (str): The user's service description
            subreddits (list): List of subreddit names to scan
            job_id (str): Optional job ID for tracking progress

        Returns:
            dict: URL to description mapping of leads
        """
        # Get job tracker if job_id is provided
        job = get_job(job_id) if job_id else None

        try:
            if job:
                job.update_status(JobStatus.PROCESSING)
                job.update_progress(10)

            print("Starting lead finding process...")

            # Step 1: Extract data from Reddit
            print("Extracting data from Reddit...")
            # Don't update progress here immediately, let get_reddit_data handle it

            posts_dict, posts_comments = await get_reddit_data(subreddits, job)
            print(
                f"Extracted {len(posts_dict)} posts and {len(posts_comments)} comments"
            )

            if job:
                job.update_results(
                    posts_processed=len(posts_dict),
                    comments_processed=len(posts_comments),
                )
                # Ensure we don't go backwards in progress
                current_progress = job.progress
                if 40 > current_progress:
                    job.update_progress(40)

            # Step 2: Find leads using AI
            print("Finding leads with AI...")
            ai_output = find_leads(user_query, posts_dict, posts_comments)
            print("AI analysis complete")

            if job:
                # Ensure we don't go backwards in progress
                current_progress = job.progress
                if 60 > current_progress:
                    job.update_progress(60)

            # Step 3: Process AI output to create URL-description mapping
            print("Processing AI output...")
            url_description_map = process_ai_output(ai_output)
            print(f"Processed {len(url_description_map)} leads")

            if job:
                job.update_results(leads_found=len(url_description_map))
                # Ensure we don't go backwards in progress
                current_progress = job.progress
                if 80 > current_progress:
                    job.update_progress(80)

            # Step 4: Save leads to database with proper URLs, subreddit names, and categories
            print("Saving leads to database...")
            # Create a mapping of IDs to full information for URL construction
            id_to_info = {}
            
            # Map post IDs to their full information
            for post in posts_dict:
                id_to_info[post["post_id"]] = {
                    "type": "post",
                    "subreddit": post["subreddit"],
                    "url": post["data"].get("url", "")
                }
            
            # Map comment IDs to their full information
            for comment in posts_comments:
                id_to_info[comment["comment_id"]] = {
                    "type": "comment",
                    "subreddit": comment["subreddit"],
                    "post_id": comment.get("post_id", "")  # This will be added later
                }
            
            # Update comment entries with their post IDs
            for post in posts_dict:
                post_id = post["post_id"]
                # Find comments that belong to this post
                for comment in posts_comments:
                    if comment.get("post_id") == post_id:
                        id_to_info[comment["comment_id"]]["post_id"] = post_id
            
            # Construct proper URLs and save leads
            final_url_description_map = {}
            subreddit_for_saving = subreddits[0] if subreddits else "unknown"
            
            # Separate leads by category for saving with proper URLs
            hot_leads = {}
            cold_leads = {}
            neutral_leads = {}
            
            for identifier, data in url_description_map.items():
                description = data['description']
                category = data.get('category', 'neutral')
                
                # Construct proper URL based on the identifier
                if identifier in id_to_info:
                    info = id_to_info[identifier]
                    if info["type"] == "post":
                        # For posts, use the actual post URL
                        url = info.get("url", f"https://www.reddit.com/r/{info['subreddit']}/comments/{identifier}")
                    else:
                        # For comments, construct the comment URL
                        post_id = info.get("post_id", "")
                        url = f"https://www.reddit.com/r/{info['subreddit']}/comments/{post_id}/_/{identifier}"
                else:
                    # Fallback URL if we don't have info
                    url = f"https://www.reddit.com/comments/{identifier}"
                
                # Create a description that includes the URL
                full_description = f"{description}\n\nURL: {url}"
                
                # Add to appropriate category dictionary
                if category == "hot":
                    hot_leads[identifier] = full_description
                elif category == "cold":
                    cold_leads[identifier] = full_description
                else:
                    neutral_leads[identifier] = full_description
            
            # Save leads by category
            if hot_leads:
                await save_leads(hot_leads, subreddits, "hot")
            if cold_leads:
                await save_leads(cold_leads, subreddits, "cold")
            if neutral_leads:
                await save_leads(neutral_leads, subreddits, "neutral")
            
            print("Leads saved successfully")

            if job:
                # Ensure we don't go backwards in progress
                current_progress = job.progress
                if 90 > current_progress:
                    job.update_progress(90)

            # Step 5: Save scanned subreddits
            if subreddits:
                for subreddit in subreddits:
                    await save_scanned_subreddit(subreddit)

            if job:
                job.mark_completed()

            return url_description_map

        except Exception as e:
            print(f"Error in lead finder: {e}")
            if job:
                # Only set error if job is not already completed
                if job.status != JobStatus.COMPLETED:
                    job.set_error(str(e))
            return {}

    async def scheduled_run(self, user_query: str):
        """
        Runs the lead finder with duplicate checking
        """
        # Get existing lead IDs from database to avoid duplicates
        existing_lead_ids = await self.get_existing_lead_ids()

        # Get subreddits to scan (from DB or default)
        subreddits = await get_scanned_subreddits()
        if not subreddits:
            subreddits = ["forhire", "slavelabour", "freelance"]

        # Run the lead finder
        url_description_map = await self.run_lead_finder(user_query, subreddits)

        # Filter out existing leads
        new_leads = {
            url: desc
            for url, desc in url_description_map.items()
            if not any(lead_id in url for lead_id in existing_lead_ids)
        }

        print(f"Found {len(new_leads)} new leads")
        return new_leads

    async def get_existing_lead_ids(self):
        """
        Get all existing lead IDs from database
        """
        async with self.SessionLocal() as session:
            from sqlalchemy import select
            from models import Lead, Comment

            # Get post IDs
            stmt = select(Lead.post_id)
            result = await session.execute(stmt)
            lead_ids = [row[0] for row in result.fetchall()]

            # Get comment IDs
            stmt = select(Comment.comment_id)
            result = await session.execute(stmt)
            comment_ids = [row[0] for row in result.fetchall()]

            return lead_ids + comment_ids


# For testing purposes
if __name__ == "__main__":
    controller = LeadlyController()
    user_query = "I am a freelance graphic designer and a full stack web developer looking for potential clients who need design or/and development services."

    # Run the controller
    result = asyncio.run(controller.run_lead_finder(user_query))
    print("Final result:", result)
