"""
Module N - Webhook Queue System
Manages failed webhooks with persistence and background retry processing
"""

import logging
import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from module_n.config import settings

logger = logging.getLogger(__name__)


class QueuedWebhookStatus(str, Enum):
    """Status of queued webhook"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueuedWebhook:
    """Queued webhook entry"""
    id: str
    event_type: str
    ingest_id: int
    payload: Dict[str, Any]
    status: QueuedWebhookStatus
    attempts: int
    max_attempts: int
    created_at: str
    last_attempt_at: Optional[str] = None
    next_retry_at: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueuedWebhook':
        """Create from dictionary"""
        return cls(**data)


class WebhookQueue:
    """
    Webhook queue manager with file-based persistence.
    Stores failed webhooks and retries them in the background.
    """
    
    def __init__(self, queue_file: Optional[str] = None):
        """
        Initialize webhook queue.
        
        Args:
            queue_file: Path to queue file (default: data/webhook_queue.json)
        """
        if queue_file:
            self.queue_file = Path(queue_file)
        else:
            self.queue_file = Path("data/webhook_queue.json")
        
        # Ensure directory exists
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load queue from file
        self.queue: List[QueuedWebhook] = []
        self._load_queue()
        
        # Background task
        self._background_task: Optional[asyncio.Task] = None
        self._running = False
    
    def _load_queue(self):
        """Load queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    self.queue = [QueuedWebhook.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self.queue)} webhooks from queue")
            except Exception as e:
                logger.error(f"Error loading webhook queue: {e}")
                self.queue = []
        else:
            self.queue = []
    
    def _save_queue(self):
        """Save queue to file"""
        try:
            with open(self.queue_file, 'w') as f:
                data = [item.to_dict() for item in self.queue]
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.queue)} webhooks to queue")
        except Exception as e:
            logger.error(f"Error saving webhook queue: {e}")
    
    def add(
        self,
        event_type: str,
        ingest_id: int,
        payload: Dict[str, Any],
        max_attempts: Optional[int] = None
    ) -> str:
        """
        Add webhook to queue.
        
        Args:
            event_type: Type of webhook event
            ingest_id: File ingest ID
            payload: Webhook payload
            max_attempts: Maximum retry attempts (default: from settings)
            
        Returns:
            Queue entry ID
        """
        # Generate unique ID
        webhook_id = f"{event_type}_{ingest_id}_{datetime.utcnow().timestamp()}"
        
        # Create queued webhook
        queued = QueuedWebhook(
            id=webhook_id,
            event_type=event_type,
            ingest_id=ingest_id,
            payload=payload,
            status=QueuedWebhookStatus.PENDING,
            attempts=0,
            max_attempts=max_attempts or settings.WEBHOOK_RETRY_ATTEMPTS,
            created_at=datetime.utcnow().isoformat()
        )
        
        # Add to queue
        self.queue.append(queued)
        self._save_queue()
        
        logger.info(f"Added webhook {webhook_id} to queue")
        return webhook_id
    
    def get_pending(self) -> List[QueuedWebhook]:
        """Get all pending webhooks ready for retry"""
        now = datetime.utcnow()
        pending = []
        
        for webhook in self.queue:
            # Skip if not pending or processing
            if webhook.status not in [QueuedWebhookStatus.PENDING, QueuedWebhookStatus.PROCESSING]:
                continue
            
            # Skip if max attempts reached
            if webhook.attempts >= webhook.max_attempts:
                webhook.status = QueuedWebhookStatus.FAILED
                continue
            
            # Check if ready for retry
            if webhook.next_retry_at:
                next_retry = datetime.fromisoformat(webhook.next_retry_at)
                if now < next_retry:
                    continue
            
            pending.append(webhook)
        
        return pending
    
    def update_status(
        self,
        webhook_id: str,
        status: QueuedWebhookStatus,
        error_message: Optional[str] = None
    ):
        """
        Update webhook status.
        
        Args:
            webhook_id: Queue entry ID
            status: New status
            error_message: Optional error message
        """
        for webhook in self.queue:
            if webhook.id == webhook_id:
                webhook.status = status
                webhook.last_attempt_at = datetime.utcnow().isoformat()
                webhook.attempts += 1
                
                if error_message:
                    webhook.error_message = error_message
                
                # Calculate next retry time with exponential backoff
                if status == QueuedWebhookStatus.PENDING and webhook.attempts < webhook.max_attempts:
                    delay = settings.WEBHOOK_RETRY_DELAY * (2 ** webhook.attempts)
                    next_retry = datetime.utcnow() + timedelta(seconds=delay)
                    webhook.next_retry_at = next_retry.isoformat()
                
                self._save_queue()
                break
    
    def remove(self, webhook_id: str):
        """Remove webhook from queue"""
        self.queue = [w for w in self.queue if w.id != webhook_id]
        self._save_queue()
        logger.info(f"Removed webhook {webhook_id} from queue")
    
    def cleanup_completed(self, max_age_hours: int = 24):
        """
        Remove completed webhooks older than max_age_hours.
        
        Args:
            max_age_hours: Maximum age in hours for completed webhooks
        """
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        original_count = len(self.queue)
        
        self.queue = [
            w for w in self.queue
            if w.status != QueuedWebhookStatus.COMPLETED
            or datetime.fromisoformat(w.created_at) > cutoff
        ]
        
        removed = original_count - len(self.queue)
        if removed > 0:
            self._save_queue()
            logger.info(f"Cleaned up {removed} completed webhooks")
    
    def get_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        stats = {
            "total": len(self.queue),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0
        }
        
        for webhook in self.queue:
            if webhook.status == QueuedWebhookStatus.PENDING:
                stats["pending"] += 1
            elif webhook.status == QueuedWebhookStatus.PROCESSING:
                stats["processing"] += 1
            elif webhook.status == QueuedWebhookStatus.COMPLETED:
                stats["completed"] += 1
            elif webhook.status == QueuedWebhookStatus.FAILED:
                stats["failed"] += 1
        
        return stats
    
    async def process_queue(self):
        """Process pending webhooks in the queue"""
        from module_n.webhooks.notifier import send_webhook_with_retry
        from module_n.webhooks.notifier import WebhookEventType
        from module_n.db.operations import get_file_ingest
        
        pending = self.get_pending()
        
        if not pending:
            return
        
        logger.info(f"Processing {len(pending)} pending webhooks")
        
        for webhook in pending:
            try:
                # Mark as processing
                webhook.status = QueuedWebhookStatus.PROCESSING
                self._save_queue()
                
                # Get file ingest
                file_ingest = get_file_ingest(webhook.ingest_id)
                if not file_ingest:
                    logger.error(f"File ingest {webhook.ingest_id} not found, removing from queue")
                    self.remove(webhook.id)
                    continue
                
                # Send webhook (without retry since queue handles retries)
                event_type = WebhookEventType(webhook.event_type)
                success = await send_webhook_with_retry(
                    event_type=event_type,
                    file_ingest=file_ingest,
                    retry=False  # Don't retry, queue will handle it
                )
                
                if success:
                    self.update_status(webhook.id, QueuedWebhookStatus.COMPLETED)
                    logger.info(f"Successfully processed queued webhook {webhook.id}")
                else:
                    # Check if max attempts reached
                    if webhook.attempts + 1 >= webhook.max_attempts:
                        self.update_status(
                            webhook.id,
                            QueuedWebhookStatus.FAILED,
                            "Max retry attempts reached"
                        )
                        logger.error(f"Webhook {webhook.id} failed after {webhook.max_attempts} attempts")
                    else:
                        self.update_status(
                            webhook.id,
                            QueuedWebhookStatus.PENDING,
                            "Webhook send failed, will retry"
                        )
                
            except Exception as e:
                logger.error(f"Error processing webhook {webhook.id}: {e}")
                self.update_status(
                    webhook.id,
                    QueuedWebhookStatus.PENDING,
                    str(e)
                )
    
    async def start_background_processing(self, interval: int = 60):
        """
        Start background task to process queue periodically.
        
        Args:
            interval: Processing interval in seconds (default: 60)
        """
        if self._running:
            logger.warning("Background processing already running")
            return
        
        self._running = True
        logger.info(f"Starting webhook queue background processing (interval: {interval}s)")
        
        while self._running:
            try:
                await self.process_queue()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in background processing: {e}")
                await asyncio.sleep(interval)
    
    def stop_background_processing(self):
        """Stop background processing"""
        self._running = False
        logger.info("Stopping webhook queue background processing")


# Global queue instance
_global_queue: Optional[WebhookQueue] = None


def get_webhook_queue() -> WebhookQueue:
    """Get global webhook queue instance"""
    global _global_queue
    if _global_queue is None:
        _global_queue = WebhookQueue()
    return _global_queue

