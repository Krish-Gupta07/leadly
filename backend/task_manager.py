import asyncio
from typing import Dict
from job_tracker import get_job

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
    
    def add_task(self, job_id: str, task: asyncio.Task):
        """Add a task to the manager"""
        self.tasks[job_id] = task
        # Remove task from manager when it's done
        task.add_done_callback(lambda t: self.remove_task(job_id))
    
    def remove_task(self, job_id: str):
        """Remove a task from the manager"""
        if job_id in self.tasks:
            del self.tasks[job_id]
    
    def get_task(self, job_id: str) -> asyncio.Task:
        """Get a task by job ID"""
        return self.tasks.get(job_id)
    
    def cancel_task(self, job_id: str):
        """Cancel a task by job ID"""
        task = self.tasks.get(job_id)
        if task:
            task.cancel()
            self.remove_task(job_id)

# Global task manager instance
task_manager = TaskManager()