from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from db import (
    get_scanned_subreddits,
    save_scanned_subreddit,
    get_leads as db_get_leads,
)
from controller import LeadlyController
from job_tracker import create_job, get_job, JobStatus
from scheduler import run_scheduled_job
from task_manager import task_manager

load_dotenv()

app = FastAPI(
    title="Leadly API",
    description="API for finding potential leads on Reddit using AI-powered analysis",
    version="1.0.0",
)

# Background task for scheduler
scheduler_task = None


@app.on_event("startup")
async def startup_event():
    """Initialize any background tasks on startup"""
    print("Leadly API started successfully")


# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize controller
controller = LeadlyController()


# Pydantic models for request/response validation
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


class LeadResponse(BaseModel):
    id: int
    post_id: str
    title: str
    post_text: Optional[str]
    url: str
    subreddit_name: str
    created_at: datetime
    updated_at: datetime


class LeadsResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    limit: int
    offset: int


class DeleteResponse(BaseModel):
    message: str


class BulkDeleteRequest(BaseModel):
    lead_ids: List[int]


class BulkDeleteResponse(BaseModel):
    message: str
    deleted_count: int


class SearchRequest(BaseModel):
    subreddits: List[str]
    limit_per_subreddit: int = 10
    keywords: List[str] = []
    user_query: str = ""


class SearchResponse(BaseModel):
    message: str
    job_id: str


class SearchStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    results: Optional[dict]
    error: Optional[str]


class SubredditsResponse(BaseModel):
    subreddits: List[str]


class AddSubredditRequest(BaseModel):
    subreddit: str


class AddSubredditResponse(BaseModel):
    message: str


class AddKeywordRequest(BaseModel):
    keyword: str


class AddKeywordResponse(BaseModel):
    message: str


class KeywordsResponse(BaseModel):
    keywords: List[str]


class ScheduleResponse(BaseModel):
    enabled: bool
    interval_minutes: int
    last_run: Optional[datetime]
    next_run: Optional[datetime]


class UpdateScheduleRequest(BaseModel):
    enabled: bool
    interval_minutes: int


class UpdateScheduleResponse(BaseModel):
    message: str


class StatsResponse(BaseModel):
    total_leads: int
    leads_by_subreddit: dict
    leads_by_source: dict
    last_scan: Optional[datetime]
    database_size: str


# Simple API key storage (in production, this should be in a database)
VALID_API_KEYS = {"dev-key": "developer", "admin-key": "administrator"}


# Dependency for API key authentication
def verify_api_key(authorization: str = Header(None)):
    print(f"Received authorization header: {authorization}")
    if not authorization:
        print("No authorization header provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract API key from "Bearer <key>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if API key is valid
    print(f"Checking token: {token}")
    if token not in VALID_API_KEYS:
        print(f"Invalid API key: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"API key verified: {token}")
    return token


# Health check endpoint
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Check if the API is running."""
    return HealthResponse(status="ok", timestamp=datetime.utcnow())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
@app.get("/api/v1/leads", response_model=LeadsResponse)
async def get_leads(
    limit: int = 100,
    offset: int = 0,
    subreddit: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[int] = None,
    api_key: str = Depends(verify_api_key),
):
    """Retrieve all leads from the database."""
    # Fetch leads from database
    leads = await db_get_leads(limit=limit, offset=offset)

    # Convert to response format
    lead_responses = [
        LeadResponse(
            id=lead.id,
            post_id=lead.post_id,
            title=lead.title,
            post_text=lead.post_text,
            url=lead.url,
            subreddit_name=lead.subreddit_name,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )
        for lead in leads
    ]

    return LeadsResponse(
        leads=lead_responses, total=len(lead_responses), limit=limit, offset=offset
    )


# Get lead by ID
@app.get("/api/v1/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, api_key: str = Depends(verify_api_key)):
    """Retrieve a specific lead by its ID."""
    # This is a simplified implementation
    raise HTTPException(status_code=404, detail="Lead not found")


# Delete lead
@app.delete("/api/v1/leads/{lead_id}", response_model=DeleteResponse)
async def delete_lead(lead_id: int, api_key: str = Depends(verify_api_key)):
    """Delete a specific lead by its ID."""
    # This is a simplified implementation
    return DeleteResponse(message="Lead deleted successfully")


# Bulk delete leads
@app.delete("/api/v1/leads", response_model=BulkDeleteResponse)
async def bulk_delete_leads(
    request: BulkDeleteRequest, api_key: str = Depends(verify_api_key)
):
    """Delete multiple leads by their IDs."""
    # This is a simplified implementation
    return BulkDeleteResponse(
        message="Leads deleted successfully", deleted_count=len(request.lead_ids)
    )


# Manual lead search
@app.post("/api/v1/reddit/search", response_model=SearchResponse)
async def manual_lead_search(
    request: SearchRequest, api_key: str = Depends(verify_api_key)
):
    """Manually trigger a search for leads on Reddit."""
    print(f"Received search request: {request}")
    print(f"API key used: {api_key}")
    try:
        # Validate input
        if not request.subreddits:
            raise HTTPException(
                status_code=400, detail="At least one subreddit is required"
            )

        if not request.user_query.strip():
            raise HTTPException(status_code=400, detail="User query is required")

        # Create a job for tracking
        job = create_job()
        print(f"Created job {job.job_id} for search request")

        # Run the lead finder in the background with job tracking
        task = asyncio.create_task(
            run_lead_finder_with_error_handling(
                request.user_query, request.subreddits, job.job_id
            )
        )
        print(f"Created task {task} for job {job.job_id}")
        
        # Add task to task manager
        task_manager.add_task(job.job_id, task)

        response = SearchResponse(
            message="Search initiated successfully", job_id=job.job_id
        )
        print(f"Sending response: {response}")
        return response

    except HTTPException as e:
        print(f"HTTP Exception in search endpoint: {e.detail}")
        raise
    except Exception as e:
        print(f"Failed to initiate search: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to initiate search: {str(e)}"
        )


async def run_lead_finder_with_error_handling(
    user_query: str, subreddits: List[str], job_id: str
):
    """Wrapper function to run lead finder with proper error handling"""
    print(f"Starting run_lead_finder_with_error_handling for job {job_id}")
    try:
        await controller.run_lead_finder(
            user_query=user_query,
            subreddits=subreddits,
            job_id=job_id,
        )
        print(f"Completed run_lead_finder_with_error_handling for job {job_id}")
    except Exception as e:
        print(f"Lead finder failed for job {job_id}: {str(e)}")
        # Update job status to failed
        job = get_job(job_id)
        if job:
            job.set_error(str(e))


# Get search status
@app.get("/api/v1/reddit/search/{job_id}", response_model=SearchStatusResponse)
async def get_search_status(job_id: str, api_key: str = Depends(verify_api_key)):
    """Get the status of a manual search job."""
    try:
        job = get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return SearchStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            results=job.results,
            error=job.error,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get job status: {str(e)}"
        )


# Get subreddits
@app.get("/api/v1/config/subreddits", response_model=SubredditsResponse)
async def get_subreddits(api_key: str = Depends(verify_api_key)):
    """Get the list of configured subreddits to monitor."""
    # This is a simplified implementation
    subreddits = await get_scanned_subreddits()
    return SubredditsResponse(subreddits=subreddits if subreddits else [])


# Add subreddit
@app.post("/api/v1/config/subreddits", response_model=AddSubredditResponse)
async def add_subreddit(
    request: AddSubredditRequest, api_key: str = Depends(verify_api_key)
):
    """Add a subreddit to monitor."""
    await save_scanned_subreddit(request.subreddit)
    return AddSubredditResponse(message="Subreddit added successfully")


# Remove subreddit
@app.delete(
    "/api/v1/config/subreddits/{subreddit}", response_model=AddSubredditResponse
)
async def remove_subreddit(subreddit: str, api_key: str = Depends(verify_api_key)):
    """Remove a subreddit from monitoring."""
    # This is a simplified implementation
    return AddSubredditResponse(message="Subreddit removed successfully")


# Get keywords
@app.get("/api/v1/config/keywords", response_model=KeywordsResponse)
async def get_keywords(api_key: str = Depends(verify_api_key)):
    """Get the list of keywords to search for."""
    # This is a simplified implementation
    return KeywordsResponse(keywords=[])


# Add keyword
@app.post("/api/v1/config/keywords", response_model=AddKeywordResponse)
async def add_keyword(
    request: AddKeywordRequest, api_key: str = Depends(verify_api_key)
):
    """Add a keyword to search for."""
    # This is a simplified implementation
    return AddKeywordResponse(message="Keyword added successfully")


# Remove keyword
@app.delete("/api/v1/config/keywords/{keyword}", response_model=AddKeywordResponse)
async def remove_keyword(keyword: str, api_key: str = Depends(verify_api_key)):
    """Remove a keyword from the search list."""
    # This is a simplified implementation
    return AddKeywordResponse(message="Keyword removed successfully")


# Get schedule
@app.get("/api/v1/schedule", response_model=ScheduleResponse)
async def get_schedule(api_key: str = Depends(verify_api_key)):
    """Get the current scheduling configuration."""
    # This is a simplified implementation
    return ScheduleResponse(
        enabled=True, interval_minutes=60, last_run=None, next_run=None
    )


# Update schedule
@app.put("/api/v1/schedule", response_model=UpdateScheduleResponse)
async def update_schedule(
    request: UpdateScheduleRequest, api_key: str = Depends(verify_api_key)
):
    """Update the scheduling configuration."""
    # This is a simplified implementation
    return UpdateScheduleResponse(message="Schedule updated successfully")


# Run scheduler now
@app.post("/api/v1/schedule/run", response_model=UpdateScheduleResponse)
async def run_scheduler_now(api_key: str = Depends(verify_api_key)):
    """Manually trigger the scheduled task."""
    # Run the scheduler in the background
    asyncio.create_task(run_scheduled_job_wrapper())
    return UpdateScheduleResponse(message="Scheduler started successfully")


async def run_scheduled_job_wrapper():
    """Wrapper to run the scheduled job and handle exceptions"""
    try:
        await run_scheduled_job()
        print("Scheduler completed successfully")
    except Exception as e:
        print(f"Scheduler failed: {str(e)}")


# Get system stats
@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_system_stats(api_key: str = Depends(verify_api_key)):
    """Get system statistics and metrics."""
    # This is a simplified implementation
    return StatsResponse(
        total_leads=0,
        leads_by_subreddit={},
        leads_by_source={"post": 0, "comment": 0},
        last_scan=None,
        database_size="0 MB",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
