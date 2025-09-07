import asyncio
import schedule
import time
from controller import LeadlyController

# User query for lead finding
USER_QUERY = "I am a freelance graphic designer and a full stack web developer looking for potential clients who need design or/and development services."


async def run_scheduled_job():
    """
    Run the scheduled lead finder job
    """
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


def run_scheduler():
    """
    Run the lead finder every 6 hours
    """

    async def job():
        await run_scheduled_job()

    # Schedule the job every 6 hours
    schedule.every(6).hours.do(lambda: asyncio.run(job()))

    print("Scheduler started. Running lead finder every 6 hours.")
    print("First run will happen in 6 hours. Press Ctrl+C to stop.")

    # Run the first job immediately
    print("Running initial lead finder...")
    asyncio.run(run_scheduled_job())

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    run_scheduler()
