"""
Module N - Webhook Notifier v2 (with retry logic and advanced features)
Sends HTTP POST notifications to Laser OS when files are processed
"""

import logging
import asyncio
import hmac
import hashlib
import httpx
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

from module_n.config import settings
from module_n.db.models import FileIngest

logger = logging.getLogger(__name__)


class WebhookEventType(str, Enum):
    """Webhook event types"""
    FILE_INGESTED = "file.ingested"
    FILE_PROCESSED = "file.processed"
    FILE_FAILED = "file.failed"
    FILE_RE_EXTRACTED = "file.re_extracted"
    FILE_DELETED = "file.deleted"


class WebhookEvent(BaseModel):
    """Webhook event payload"""
    event_type: WebhookEventType
    timestamp: str
    ingest_id: int
    file_data: Dict[str, Any]
    
    class Config:
        use_enum_values = True


def generate_webhook_signature(payload: str, secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for webhook payload.
    
    Args:
        payload: JSON string of the webhook payload
        secret: Secret key for signing
        
    Returns:
        Hex digest of the signature
    """
    return hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def should_send_event(event_type: WebhookEventType) -> bool:
    """
    Check if event type should be sent based on configuration.
    
    Args:
        event_type: Type of webhook event
        
    Returns:
        True if event should be sent, False otherwise
    """
    # Get enabled event types from settings
    enabled_events = getattr(settings, 'WEBHOOK_ENABLED_EVENTS', None)
    
    # If not configured, send all events
    if not enabled_events:
        return True
    
    # Check if event type is in enabled list
    return event_type.value in enabled_events


async def send_webhook_with_retry(
    event_type: WebhookEventType,
    file_ingest: FileIngest,
    additional_data: Optional[Dict[str, Any]] = None,
    retry: bool = True
) -> bool:
    """
    Send webhook notification to Laser OS with automatic retry logic and exponential backoff.
    
    Args:
        event_type: Type of webhook event
        file_ingest: FileIngest database record
        additional_data: Optional additional data to include
        retry: Whether to retry on failure (default: True)
        
    Returns:
        True if webhook sent successfully, False otherwise
    """
    if not settings.LASER_OS_WEBHOOK_URL:
        logger.warning("Webhook URL not configured, skipping notification")
        return False
    
    # Check if event type should be sent
    if not should_send_event(event_type):
        logger.debug(f"Event type {event_type.value} is filtered out, skipping")
        return True  # Return True to not treat as error
    
    # Build webhook payload
    file_data = {
        "ingest_id": file_ingest.id,
        "original_filename": file_ingest.original_filename,
        "stored_filename": file_ingest.stored_filename,
        "file_path": file_ingest.file_path,
        "file_type": file_ingest.file_type,
        "file_size": file_ingest.file_size,
        "status": file_ingest.status,
        "confidence_score": file_ingest.confidence_score,
        "client_code": file_ingest.client_code,
        "project_code": file_ingest.project_code,
        "part_name": file_ingest.part_name,
        "material": file_ingest.material,
        "thickness_mm": file_ingest.thickness_mm,
        "quantity": file_ingest.quantity,
        "version": file_ingest.version,
        "created_at": file_ingest.created_at.isoformat() if file_ingest.created_at else None,
        "processed_at": file_ingest.processed_at.isoformat() if file_ingest.processed_at else None,
    }
    
    # Add additional data if provided
    if additional_data:
        file_data.update(additional_data)
    
    # Create webhook event
    event = WebhookEvent(
        event_type=event_type,
        timestamp=datetime.utcnow().isoformat(),
        ingest_id=file_ingest.id,
        file_data=file_data
    )
    
    # Determine retry attempts
    max_attempts = settings.WEBHOOK_RETRY_ATTEMPTS if retry else 1
    
    # Retry loop with exponential backoff
    for attempt in range(1, max_attempts + 1):
        try:
            # Log attempt
            if attempt == 1:
                logger.info(f"Sending webhook: {event_type.value} for file {file_ingest.id}")
            else:
                logger.info(f"Retry attempt {attempt}/{max_attempts} for webhook {event_type.value} file {file_ingest.id}")
            
            logger.debug(f"Webhook URL: {settings.LASER_OS_WEBHOOK_URL}")
            
            # Prepare payload
            payload_dict = event.model_dump()
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            
            # Add signature if secret is configured
            webhook_secret = getattr(settings, 'WEBHOOK_SECRET', None)
            if webhook_secret:
                import json
                payload_str = json.dumps(payload_dict, sort_keys=True)
                signature = generate_webhook_signature(payload_str, webhook_secret)
                headers["X-Webhook-Signature"] = f"sha256={signature}"
                logger.debug("Added webhook signature to headers")
            
            # Send webhook
            async with httpx.AsyncClient(timeout=settings.LASER_OS_TIMEOUT) as client:
                response = await client.post(
                    settings.LASER_OS_WEBHOOK_URL,
                    json=payload_dict,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Webhook sent successfully for file {file_ingest.id} (attempt {attempt})")
                    return True
                else:
                    logger.error(
                        f"Webhook failed with status {response.status_code}: {response.text} (attempt {attempt})"
                    )
                    
                    # Don't retry on 4xx errors (client errors)
                    if 400 <= response.status_code < 500:
                        logger.warning(f"Client error {response.status_code}, not retrying")
                        return False
                    
                    # Retry on 5xx errors (server errors)
                    if attempt < max_attempts:
                        delay = settings.WEBHOOK_RETRY_DELAY * (2 ** (attempt - 1))  # Exponential backoff
                        logger.info(f"Waiting {delay}s before retry...")
                        await asyncio.sleep(delay)
                    
        except httpx.TimeoutException:
            logger.error(f"Webhook timeout for file {file_ingest.id} (attempt {attempt})")
            if attempt < max_attempts:
                delay = settings.WEBHOOK_RETRY_DELAY * (2 ** (attempt - 1))
                logger.info(f"Waiting {delay}s before retry...")
                await asyncio.sleep(delay)
                
        except httpx.RequestError as e:
            logger.error(f"Webhook request error for file {file_ingest.id}: {e} (attempt {attempt})")
            if attempt < max_attempts:
                delay = settings.WEBHOOK_RETRY_DELAY * (2 ** (attempt - 1))
                logger.info(f"Waiting {delay}s before retry...")
                await asyncio.sleep(delay)
                
        except Exception as e:
            logger.error(f"Unexpected webhook error for file {file_ingest.id}: {e} (attempt {attempt})")
            if attempt < max_attempts:
                delay = settings.WEBHOOK_RETRY_DELAY * (2 ** (attempt - 1))
                logger.info(f"Waiting {delay}s before retry...")
                await asyncio.sleep(delay)
    
    # All retries exhausted
    logger.error(f"Webhook failed after {max_attempts} attempts for file {file_ingest.id}")
    return False


# Alias for backward compatibility
send_webhook = send_webhook_with_retry


def send_webhook_sync(
    event_type: WebhookEventType,
    file_ingest: FileIngest,
    additional_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Synchronous wrapper for send_webhook (for non-async contexts).
    
    Args:
        event_type: Type of webhook event
        file_ingest: FileIngest database record
        additional_data: Optional additional data to include
        
    Returns:
        True if webhook sent successfully, False otherwise
    """
    import asyncio
    
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run async function
        return loop.run_until_complete(
            send_webhook(event_type, file_ingest, additional_data)
        )
    except Exception as e:
        logger.error(f"Error in sync webhook wrapper: {e}")
        return False

