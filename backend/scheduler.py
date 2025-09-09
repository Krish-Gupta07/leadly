import asyncio
import schedule
import time
from datetime import datetime, timedelta
from controller import LeadlyController

# User query for lead finding
USER_QUERY = "I am a freelance graphic designer and a full stack web developer looking for potential clients who need design or/and development services."

# Global variable to track next run time
next_run_time = None


async def run_scheduled_job():
    """
    Run the scheduled lead finder job
    """
    global next_run_time
    controller = LeadlyController()
    print("Running scheduled lead finder...")
    try:
        new_leads = await controller.scheduled_run(USER_QUERY)
        print(f"Found {len(new_leads)} new leads:")
        for url, description in new_leads.items():
            print(f"  {url}: {description}")
        return new_leads
    except Exception as e:
        print(f"Error in scheduled job: {e}")
        raise


def get_next_run_time():
    """
    Get the next scheduled run time
    """
    global next_run_time
    return next_run_time


def run_scheduler():
    """
    Run the lead finder every 5 minutes
    """
    global next_run_time

    async def job():
        await run_scheduled_job()

    # Schedule the job every 5 minutes
    schedule.every(5).minutes.do(lambda: asyncio.run(job()))

    print("Scheduler started. Running lead finder every 5 minutes.")
    
    # Set initial next run time
    next_run_time = datetime.now() + timedelta(minutes=5)
    print(f"Next run scheduled for: {next_run_time}")

    # Run the first job immediately
    print("Running initial lead finder...")
    asyncio.run(run_scheduled_job())
    
    # Update next run time after first run
    next_run_time = datetime.now() + timedelta(minutes=5)
    print(f"Next run scheduled for: {next_run_time}")

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second for more responsiveness
        
        # Update next run time periodically
        if schedule.jobs:
            next_run_time = schedule.jobs[0].next_run
