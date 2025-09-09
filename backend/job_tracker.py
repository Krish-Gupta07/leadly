import asyncio
import uuid
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SearchJob:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = JobStatus.PENDING
        self.progress = 0
        self.results = {
            "posts_processed": 0,
            "comments_processed": 0,
            "leads_found": 0
        }
        self.error: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_status(self, status: JobStatus):
        self.status = status
        # When marking as completed, also set progress to 100
        if status == JobStatus.COMPLETED:
            self.progress = 100
        self.updated_at = datetime.utcnow()

    def update_progress(self, progress: int):
        # Ensure progress doesn't go backwards unless we're resetting
        if progress >= self.progress or progress == 0:
            self.progress = progress
        self.updated_at = datetime.utcnow()

    def mark_completed(self):
        """Explicitly mark job as completed with proper progress"""
        self.status = JobStatus.COMPLETED
        self.progress = 100
        self.updated_at = datetime.utcnow()

    def update_results(self, posts_processed: int = 0, comments_processed: int = 0, leads_found: int = 0):
        self.results["posts_processed"] += posts_processed
        self.results["comments_processed"] += comments_processed
        self.results["leads_found"] += leads_found
        self.updated_at = datetime.utcnow()

    def set_error(self, error: str):
        self.error = error
        self.status = JobStatus.FAILED
        self.updated_at = datetime.utcnow()

# In-memory job store (in production, this should be a database)
job_store: Dict[str, SearchJob] = {}

def create_job() -> SearchJob:
    job_id = str(uuid.uuid4())
    job = SearchJob(job_id)
    job_store[job_id] = job
    return job

def get_job(job_id: str) -> Optional[SearchJob]:
    return job_store.get(job_id)

def remove_job(job_id: str):
    if job_id in job_store:
        del job_store[job_id]