"""
Background Tasks Module.

Provides a Redis-backed task queue for background job processing.

Features:
- Async task execution
- Retry with exponential backoff
- Task scheduling (delayed execution)
- Priority queues
- Task status tracking

Usage:
    from core.tasks import TaskQueue, task

    queue = TaskQueue(redis_url="redis://localhost:6379")

    @task(queue="emails", retry=3)
    async def send_email(to: str, subject: str):
        pass

    # Enqueue task
    await send_email.delay(to="user@example.com", subject="Welcome!")
"""

from core.tasks.queue import Task, TaskQueue, TaskResult, TaskStatus, task

__all__ = [
    "TaskQueue",
    "Task",
    "TaskStatus",
    "TaskResult",
    "task",
]
