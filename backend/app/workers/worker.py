import asyncio
import signal
import sys
from typing import Dict, Any
import structlog

from app.core.config import settings
from app.services.jitter_queue import jitter_queue
from app.integrations.twilio_client import TwilioClient

logger = structlog.get_logger()

class TaskWorker:
    """Worker process for handling delayed tasks from the jitter queue"""
    
    def __init__(self):
        self.running = False
        self.twilio_client = TwilioClient()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal", signal=signum)
        self.running = False
    
    async def process_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Process a single task
        
        Args:
            task_data: Task data from queue
        
        Returns:
            True if successful, False if failed (will be retried)
        """
        task_id = task_data.get("task_id")
        task_type = task_data.get("task_type")
        payload = task_data.get("payload", {})
        tenant_id = task_data.get("tenant_id")
        
        logger.info(
            "Processing task",
            task_id=task_id,
            task_type=task_type,
            tenant_id=tenant_id
        )
        
        try:
            if task_type == "MISSED_CALL_SMS":
                return await self._handle_missed_call_sms(payload, tenant_id)
            elif task_type == "REVIEW_REQUEST_SMS":
                return await self._handle_review_request_sms(payload, tenant_id)
            elif task_type == "CHATWOOT_REPLY":
                return await self._handle_chatwoot_reply(payload, tenant_id)
            else:
                logger.error(f"Unknown task type: {task_type}", task_id=task_id)
                return True  # Don't retry unknown task types
        
        except Exception as e:
            logger.error(
                "Task processing failed",
                task_id=task_id,
                task_type=task_type,
                error=str(e)
            )
            return False
    
    async def _handle_missed_call_sms(self, payload: Dict[str, Any], tenant_id: str) -> bool:
        """Handle missed call SMS automation"""
        try:
            to_number = payload.get("to_number")
            caller_name = payload.get("caller_name")
            
            if not to_number:
                logger.error("Missing to_number for missed call SMS", payload=payload)
                return True  # Don't retry malformed payloads
            
            success = await self.twilio_client.send_missed_call_followup(
                to=to_number,
                caller_name=caller_name
            )
            
            if success:
                logger.info("Missed call SMS sent", to_number=to_number, tenant_id=tenant_id)
            else:
                logger.warning("Failed to send missed call SMS", to_number=to_number)
            
            return success
            
        except Exception as e:
            logger.error("Error handling missed call SMS", error=str(e), payload=payload)
            return False
    
    async def _handle_review_request_sms(self, payload: Dict[str, Any], tenant_id: str) -> bool:
        """Handle review request SMS automation"""
        try:
            to_number = payload.get("to_number")
            customer_name = payload.get("customer_name")
            
            if not to_number:
                logger.error("Missing to_number for review request", payload=payload)
                return True  # Don't retry malformed payloads
            
            success = await self.twilio_client.send_review_request(
                to=to_number,
                customer_name=customer_name
            )
            
            if success:
                logger.info("Review request SMS sent", to_number=to_number, tenant_id=tenant_id)
            else:
                logger.warning("Failed to send review request SMS", to_number=to_number)
            
            return success
            
        except Exception as e:
            logger.error("Error handling review request SMS", error=str(e), payload=payload)
            return False
    
    async def _handle_chatwoot_reply(self, payload: Dict[str, Any], tenant_id: str) -> bool:
        """Handle Chatwoot automated reply (placeholder for future implementation)"""
        try:
            # This would integrate with Chatwoot API when implemented
            logger.info("Chatwoot reply task received", payload=payload, tenant_id=tenant_id)
            
            # For now, just log and return success
            # TODO: Implement Chatwoot API integration
            return True
            
        except Exception as e:
            logger.error("Error handling Chatwoot reply", error=str(e), payload=payload)
            return False
    
    async def run(self):
        """Main worker loop"""
        self.running = True
        logger.info("Task worker started", worker_concurrency=settings.WORKER_CONCURRENCY)
        
        while self.running:
            try:
                # Pop due tasks from queue
                tasks = jitter_queue.pop_due(batch_size=settings.WORKER_CONCURRENCY * 2)
                
                if not tasks:
                    # No tasks available, sleep briefly
                    await asyncio.sleep(settings.WORKER_POLL_INTERVAL)
                    continue
                
                # Process tasks concurrently with semaphore for rate limiting
                semaphore = asyncio.Semaphore(settings.WORKER_CONCURRENCY)
                
                async def process_with_semaphore(task_data):
                    async with semaphore:
                        success = await self.process_task(task_data)
                        if not success:
                            # Requeue failed task with exponential backoff
                            jitter_queue.requeue_failed_task(task_data)
                
                # Process all tasks concurrently
                await asyncio.gather(
                    *[process_with_semaphore(task) for task in tasks],
                    return_exceptions=True
                )
                
            except Exception as e:
                logger.error("Worker loop error", error=str(e))
                await asyncio.sleep(5)  # Brief pause on error
        
        logger.info("Task worker stopped")
    
    def stop(self):
        """Stop the worker gracefully"""
        self.running = False

async def main():
    """Entry point for the worker process"""
    logger.info("Starting Lily AI task worker")
    
    worker = TaskWorker()
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        worker.stop()
        logger.info("Worker shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())