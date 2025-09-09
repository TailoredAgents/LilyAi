import json
import time
import uuid
import redis
from typing import List, Dict, Any, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()

class JitterQueue:
    """Redis ZSET-based delayed task queue for jittered message sending"""
    
    def __init__(self):
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                # Test connection
                self.redis_client.ping()
                logger.info("Jitter queue Redis client initialized")
            except Exception as e:
                logger.error("Failed to connect to Redis", error=str(e))
        else:
            logger.warning("Redis URL not configured - jitter queue disabled")
    
    @property
    def queue_key(self) -> str:
        return "lily:jitter_queue"
    
    def enqueue_delayed(
        self,
        key: str,
        payload: Dict[str, Any],
        delay_seconds: int,
        tenant_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Enqueue a delayed task
        
        Args:
            key: Task type key (e.g., 'MISSED_CALL_SMS', 'REVIEW_REQUEST_SMS')
            payload: Task payload data
            delay_seconds: Delay before task should be processed
            tenant_id: Tenant ID for tracking
            idempotency_key: Optional key to prevent duplicates
        
        Returns:
            Task ID if successful, None if failed
        """
        if not self.redis_client:
            logger.error("Redis client not available")
            return None
        
        try:
            task_id = idempotency_key or str(uuid.uuid4())
            execute_at = time.time() + delay_seconds
            
            task_data = {
                "task_id": task_id,
                "task_type": key,
                "payload": payload,
                "tenant_id": tenant_id,
                "created_at": time.time(),
                "execute_at": execute_at,
                "retry_count": 0
            }
            
            # Add to Redis sorted set with execute_at as score
            self.redis_client.zadd(
                self.queue_key,
                {json.dumps(task_data): execute_at}
            )
            
            logger.info(
                "Task enqueued",
                task_id=task_id,
                task_type=key,
                tenant_id=tenant_id,
                delay_seconds=delay_seconds,
                execute_at=execute_at
            )
            
            return task_id
            
        except Exception as e:
            logger.error(
                "Failed to enqueue task",
                task_type=key,
                error=str(e),
                tenant_id=tenant_id
            )
            return None
    
    def pop_due(self, batch_size: int = 50) -> List[Dict[str, Any]]:
        """
        Pop tasks that are due for execution
        
        Args:
            batch_size: Maximum number of tasks to return
        
        Returns:
            List of task data dictionaries
        """
        if not self.redis_client:
            return []
        
        try:
            now = time.time()
            
            # Get tasks due for execution
            raw_tasks = self.redis_client.zrangebyscore(
                self.queue_key,
                0,
                now,
                start=0,
                num=batch_size
            )
            
            if not raw_tasks:
                return []
            
            # Remove tasks from queue atomically
            pipe = self.redis_client.pipeline()
            for raw_task in raw_tasks:
                pipe.zrem(self.queue_key, raw_task)
            pipe.execute()
            
            # Parse task data
            tasks = []
            for raw_task in raw_tasks:
                try:
                    task_data = json.loads(raw_task)
                    tasks.append(task_data)
                except json.JSONDecodeError as e:
                    logger.error("Failed to parse task data", error=str(e))
            
            if tasks:
                logger.info(f"Popped {len(tasks)} due tasks from queue")
            
            return tasks
            
        except Exception as e:
            logger.error("Failed to pop tasks from queue", error=str(e))
            return []
    
    def requeue_failed_task(
        self,
        task_data: Dict[str, Any],
        delay_seconds: int = 60
    ) -> bool:
        """
        Requeue a failed task with exponential backoff
        
        Args:
            task_data: Original task data
            delay_seconds: Base delay for retry
        
        Returns:
            True if requeued successfully
        """
        if not self.redis_client:
            return False
        
        try:
            task_data["retry_count"] = task_data.get("retry_count", 0) + 1
            max_retries = 5
            
            if task_data["retry_count"] > max_retries:
                logger.error(
                    "Task exceeded max retries, dropping",
                    task_id=task_data.get("task_id"),
                    task_type=task_data.get("task_type"),
                    retry_count=task_data["retry_count"]
                )
                return False
            
            # Exponential backoff
            backoff_delay = delay_seconds * (2 ** (task_data["retry_count"] - 1))
            execute_at = time.time() + backoff_delay
            task_data["execute_at"] = execute_at
            
            # Re-add to queue
            self.redis_client.zadd(
                self.queue_key,
                {json.dumps(task_data): execute_at}
            )
            
            logger.info(
                "Task requeued for retry",
                task_id=task_data.get("task_id"),
                retry_count=task_data["retry_count"],
                backoff_delay=backoff_delay
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to requeue task",
                task_id=task_data.get("task_id"),
                error=str(e)
            )
            return False
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        if not self.redis_client:
            return {"total": 0, "due": 0, "pending": 0}
        
        try:
            now = time.time()
            total = self.redis_client.zcard(self.queue_key)
            due = self.redis_client.zcount(self.queue_key, 0, now)
            
            return {
                "total": total,
                "due": due,
                "pending": total - due
            }
            
        except Exception as e:
            logger.error("Failed to get queue stats", error=str(e))
            return {"total": 0, "due": 0, "pending": 0}

# Global instance
jitter_queue = JitterQueue()