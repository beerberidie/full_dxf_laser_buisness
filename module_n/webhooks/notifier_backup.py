"""
Module N - Webhook Notifier
Sends HTTP POST notifications to Laser OS when files are processed
"""

import logging
import asyncio
import httpx
from enum import Enum
from typing import Optional, Dict, Any
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


async def send_webhook(
    event_type: WebhookEventType,
    file_ingest: FileIngest,
    additional_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send webhook notification to Laser OS.
    
    Args:
        event_type: Type of webhook event
        file_ingest: FileIngest database record
        additional_data: Optional additional data to include
        
    Returns:
        True if webhook sent successfully, False otherwise
    """
    if not settings.LASER_OS_WEBHOOK_URL:
        logger.warning("Webhook URL not configured, skipping notification")
        return False
    
    try:
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
        
        # Send webhook
        logger.info(f"Sending webhook: {event_type.value} for file {file_ingest.id}")
        logger.debug(f"Webhook URL: {settings.LASER_OS_WEBHOOK_URL}")
        
        async with httpx.AsyncClient(timeout=settings.LASER_OS_TIMEOUT) as client:
            response = await client.post(
                settings.LASER_OS_WEBHOOK_URL,
                json=event.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook sent successfully for file {file_ingest.id}")
                return True
            else:
                logger.error(
                    f"Webhook failed with status {response.status_code}: {response.text}"
                )
                return False
                
    except httpx.TimeoutException:
        logger.error(f"Webhook timeout for file {file_ingest.id}")
        return False
    except httpx.RequestError as e:
        logger.error(f"Webhook request error for file {file_ingest.id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending webhook for file {file_ingest.id}: {e}")
        return False


def send_webhook_sync(
    event_type: WebhookEventType,
    file_ingest: FileIngest,
    additional_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send webhook notification synchronously (for non-async contexts).
    
    Args:
        event_type: Type of webhook event
        file_ingest: FileIngest database record
        additional_data: Optional additional data to include
        
    Returns:
        True if webhook sent successfully, False otherwise
    """
    if not settings.LASER_OS_WEBHOOK_URL:
        logger.warning("Webhook URL not configured, skipping notification")
        return False
    
    try:
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
        
        # Send webhook
        logger.info(f"Sending webhook: {event_type.value} for file {file_ingest.id}")
        logger.debug(f"Webhook URL: {settings.LASER_OS_WEBHOOK_URL}")
        
        with httpx.Client(timeout=settings.LASER_OS_TIMEOUT) as client:
            response = client.post(
                settings.LASER_OS_WEBHOOK_URL,
                json=event.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook sent successfully for file {file_ingest.id}")
                return True
            else:
                logger.error(
                    f"Webhook failed with status {response.status_code}: {response.text}"
                )
                return False
                
    except httpx.TimeoutException:
        logger.error(f"Webhook timeout for file {file_ingest.id}")
        return False
    except httpx.RequestError as e:
        logger.error(f"Webhook request error for file {file_ingest.id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending webhook for file {file_ingest.id}: {e}")
        return False

