"""
Task Queue Implementation.

Provides a Redis-backed task queue for background processing.
"""

import asyncio
import functools
import json
import pickle
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

from loguru import logger


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """
    Represents a background task.

    Attributes:
        id: Unique task identifier.
        name: Task function name.
        queue: Queue name.
        args: Positional arguments.
        kwargs: Keyword arguments.
        status: Current status.
        created_at: Creation timestamp.
        started_at: Execution start timestamp.
        completed_at: Completion timestamp.
        result: Task result or error.
        attempts: Number of execution attempts.
        max_retries: Maximum retry attempts.
        retry_delay: Delay between retries in seconds.
        priority: Task priority (higher = more important).
        scheduled_at: Scheduled execution time.
    """

    id: str
    name: str
    queue: str = "default"
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    attempts: int = 0
    max_retries: int = 3
    retry_delay: float = 60.0
    priority: int = 0
    scheduled_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "queue": self.queue,
            "args": list(self.args),
            "kwargs": self.kwargs,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": str(self.result) if self.result else None,
            "error": self.error,
            "attempts": self.attempts,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "priority": self.priority,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            queue=data.get("queue", "default"),
            args=tuple(data.get("args", [])),
            kwargs=data.get("kwargs", {}),
            status=TaskStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            result=data.get("result"),
            error=data.get("error"),
            attempts=data.get("attempts", 0),
            max_retries=data.get("max_retries", 3),
            retry_delay=data.get("retry_delay", 60.0),
            priority=data.get("priority", 0),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data.get("scheduled_at") else None,
        )


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None


class TaskStore:
    """Base class for task storage."""

    async def enqueue(self, task: Task) -> None:
        """Add task to queue."""
        pass

    async def dequeue(self, queue: str) -> Optional[Task]:
        """Get next task from queue."""
        pass

    async def get(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        pass

    async def update(self, task: Task) -> None:
        """Update task state."""
        pass

    async def get_pending_count(self, queue: str) -> int:
        """Get count of pending tasks."""
        return 0


class InMemoryTaskStore(TaskStore):
    """In-memory task store (for development/testing)."""

    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._queues: dict[str, list[str]] = {}
        self._lock = asyncio.Lock()

    async def enqueue(self, task: Task) -> None:
        """Add task to queue."""
        async with self._lock:
            self._tasks[task.id] = task
            if task.queue not in self._queues:
                self._queues[task.queue] = []
            # Insert based on priority (higher priority first)
            inserted = False
            for i, task_id in enumerate(self._queues[task.queue]):
                existing = self._tasks.get(task_id)
                if existing and task.priority > existing.priority:
                    self._queues[task.queue].insert(i, task.id)
                    inserted = True
                    break
            if not inserted:
                self._queues[task.queue].append(task.id)

    async def dequeue(self, queue: str) -> Optional[Task]:
        """Get next task from queue."""
        async with self._lock:
            if queue not in self._queues or not self._queues[queue]:
                return None
            task_id = self._queues[queue].pop(0)
            return self._tasks.get(task_id)

    async def get(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)

    async def update(self, task: Task) -> None:
        """Update task state."""
        async with self._lock:
            self._tasks[task.id] = task

    async def get_pending_count(self, queue: str) -> int:
        """Get count of pending tasks."""
        return len(self._queues.get(queue, []))


class RedisTaskStore(TaskStore):
    """Redis-backed task store."""

    def __init__(self, redis_client: Any):
        self._redis = redis_client
        self._task_prefix = "task:"
        self._queue_prefix = "queue:"

    async def enqueue(self, task: Task) -> None:
        """Add task to queue."""
        # Store task data
        task_key = f"{self._task_prefix}{task.id}"
        self._redis.set(task_key, json.dumps(task.to_dict()))

        # Add to queue (sorted set with priority as score)
        queue_key = f"{self._queue_prefix}{task.queue}"
        self._redis.zadd(queue_key, {task.id: -task.priority})

    async def dequeue(self, queue: str) -> Optional[Task]:
        """Get next task from queue."""
        queue_key = f"{self._queue_prefix}{queue}"

        # Get and remove highest priority task
        result = self._redis.zpopmin(queue_key)
        if not result:
            return None

        task_id = result[0][0] if isinstance(result[0], tuple) else result[0]
        return await self.get(task_id)

    async def get(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        task_key = f"{self._task_prefix}{task_id}"
        data = self._redis.get(task_key)
        if data:
            return Task.from_dict(json.loads(data))
        return None

    async def update(self, task: Task) -> None:
        """Update task state."""
        task_key = f"{self._task_prefix}{task.id}"
        self._redis.set(task_key, json.dumps(task.to_dict()))

    async def get_pending_count(self, queue: str) -> int:
        """Get count of pending tasks."""
        queue_key = f"{self._queue_prefix}{queue}"
        return self._redis.zcard(queue_key)


class TaskQueue:
    """
    Background task queue manager.

    Usage:
        queue = TaskQueue()

        # Register task handlers
        @queue.task(name="send_email")
        async def send_email(to: str, subject: str):
            pass

        # Enqueue task
        task_id = await queue.enqueue(
            "send_email",
            kwargs={"to": "user@example.com", "subject": "Hello"}
        )

        # Start worker (in separate process/thread)
        await queue.worker("default")
    """

    def __init__(
        self,
        store: Optional[TaskStore] = None,
        default_retry: int = 3,
        default_retry_delay: float = 60.0,
    ):
        """
        Initialize task queue.

        Args:
            store: Task store implementation.
            default_retry: Default retry count.
            default_retry_delay: Default retry delay in seconds.
        """
        self._store = store or InMemoryTaskStore()
        self._handlers: dict[str, Callable] = {}
        self._default_retry = default_retry
        self._default_retry_delay = default_retry_delay
        self._running = False

    def register(
        self,
        name: str,
        handler: Callable,
        retry: Optional[int] = None,
        retry_delay: Optional[float] = None,
    ) -> None:
        """Register a task handler."""
        self._handlers[name] = handler

    def task(
        self,
        name: Optional[str] = None,
        queue: str = "default",
        retry: Optional[int] = None,
        retry_delay: Optional[float] = None,
        priority: int = 0,
    ) -> Callable:
        """
        Decorator to register a task handler.

        Usage:
            @queue.task(name="send_email", retry=3)
            async def send_email(to: str):
                pass
        """

        def decorator(func: Callable) -> Callable:
            task_name = name or func.__name__
            self._handlers[task_name] = func

            # Add delay method for async enqueueing
            async def delay(*args: Any, **kwargs: Any) -> str:
                return await self.enqueue(
                    task_name,
                    args=args,
                    kwargs=kwargs,
                    queue=queue,
                    retry=retry or self._default_retry,
                    retry_delay=retry_delay or self._default_retry_delay,
                    priority=priority,
                )

            func.delay = delay
            func.task_name = task_name
            return func

        return decorator

    async def enqueue(
        self,
        name: str,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        queue: str = "default",
        retry: Optional[int] = None,
        retry_delay: Optional[float] = None,
        priority: int = 0,
        delay: Optional[float] = None,
        scheduled_at: Optional[datetime] = None,
    ) -> str:
        """
        Enqueue a task for execution.

        Args:
            name: Task handler name.
            args: Positional arguments.
            kwargs: Keyword arguments.
            queue: Queue name.
            retry: Max retry attempts.
            retry_delay: Retry delay in seconds.
            priority: Task priority.
            delay: Delay execution by N seconds.
            scheduled_at: Schedule for specific time.

        Returns:
            Task ID.
        """
        task_id = str(uuid.uuid4())

        if delay:
            scheduled_at = datetime.utcnow() + timedelta(seconds=delay)

        task = Task(
            id=task_id,
            name=name,
            queue=queue,
            args=args,
            kwargs=kwargs or {},
            max_retries=retry or self._default_retry,
            retry_delay=retry_delay or self._default_retry_delay,
            priority=priority,
            scheduled_at=scheduled_at,
        )

        await self._store.enqueue(task)
        logger.debug(f"Enqueued task {task_id}: {name}")
        return task_id

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return await self._store.get(task_id)

    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute a single task."""
        handler = self._handlers.get(task.name)
        if not handler:
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"No handler registered for task: {task.name}",
            )

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        task.attempts += 1
        await self._store.update(task)

        start_time = time.perf_counter()

        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(*task.args, **task.kwargs)
            else:
                result = handler(*task.args, **task.kwargs)

            duration = (time.perf_counter() - start_time) * 1000

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            await self._store.update(task)

            return TaskResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                result=result,
                duration_ms=duration,
            )

        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Task {task.id} failed: {e}")

            if task.attempts < task.max_retries:
                task.status = TaskStatus.RETRYING
                task.error = str(e)
                task.scheduled_at = datetime.utcnow() + timedelta(
                    seconds=task.retry_delay * task.attempts
                )
                await self._store.update(task)
                await self._store.enqueue(task)

                return TaskResult(
                    task_id=task.id,
                    status=TaskStatus.RETRYING,
                    error=str(e),
                    duration_ms=duration,
                )
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = str(e)
                await self._store.update(task)

                return TaskResult(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=str(e),
                    duration_ms=duration,
                )

    async def worker(
        self,
        queue: str = "default",
        poll_interval: float = 1.0,
    ) -> None:
        """
        Start a worker to process tasks.

        Args:
            queue: Queue to process.
            poll_interval: Seconds between polling for tasks.
        """
        self._running = True
        logger.info(f"Starting worker for queue: {queue}")

        while self._running:
            task = await self._store.dequeue(queue)

            if task:
                # Check if task is scheduled for later
                if task.scheduled_at and task.scheduled_at > datetime.utcnow():
                    await self._store.enqueue(task)
                    await asyncio.sleep(poll_interval)
                    continue

                result = await self._execute_task(task)
                logger.debug(f"Task {task.id} completed: {result.status}")
            else:
                await asyncio.sleep(poll_interval)

    def stop(self) -> None:
        """Stop the worker."""
        self._running = False


# Global task queue instance
_task_queue: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """Get global task queue instance."""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue


def task(
    name: Optional[str] = None,
    queue: str = "default",
    retry: int = 3,
    retry_delay: float = 60.0,
    priority: int = 0,
) -> Callable:
    """
    Decorator to register a task with the global queue.

    Usage:
        @task(name="send_email", retry=3)
        async def send_email(to: str):
            pass

        await send_email.delay(to="user@example.com")
    """
    return get_task_queue().task(
        name=name,
        queue=queue,
        retry=retry,
        retry_delay=retry_delay,
        priority=priority,
    )
