"""
Module N - Advanced Webhook Tests
Tests for retry logic, queue, signatures, filtering, and monitoring
"""

import pytest
import httpx
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from module_n.webhooks import (
    send_webhook_with_retry,
    WebhookEventType,
    generate_webhook_signature,
    should_send_event,
    WebhookQueue,
    QueuedWebhookStatus,
    WebhookMonitor
)
from module_n.db.models import FileIngest
from module_n.config import settings


@pytest.fixture
def mock_file_ingest():
    """Create a mock FileIngest object for testing"""
    file_ingest = MagicMock(spec=FileIngest)
    file_ingest.id = 123
    file_ingest.original_filename = "test.dxf"
    file_ingest.stored_filename = "CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf"
    file_ingest.file_path = "CL0001/JB-2025-10-CL0001-001/CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf"
    file_ingest.file_type = "dxf"
    file_ingest.file_size = 12345
    file_ingest.status = "completed"
    file_ingest.confidence_score = 0.95
    file_ingest.client_code = "CL0001"
    file_ingest.project_code = "JB-2025-10-CL0001-001"
    file_ingest.part_name = "Bracket"
    file_ingest.material = "Mild Steel"
    file_ingest.thickness_mm = 5.0
    file_ingest.quantity = 10
    file_ingest.version = 1
    file_ingest.created_at = datetime(2025, 10, 21, 10, 29, 0)
    file_ingest.processed_at = datetime(2025, 10, 21, 10, 30, 0)
    return file_ingest


# ============================================================================
# RETRY LOGIC TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_retry_on_server_error(mock_file_ingest):
    """Test retry logic on 5xx server errors"""
    with patch('httpx.AsyncClient') as mock_client:
        # First attempt: 500 error, second attempt: success
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = 'Internal Server Error'
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        
        mock_post = AsyncMock(side_effect=[mock_response_fail, mock_response_success])
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Send webhook with retry
        result = await send_webhook_with_retry(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest,
            retry=True
        )
        
        assert result is True
        assert mock_post.call_count == 2  # Should retry once


@pytest.mark.asyncio
async def test_no_retry_on_client_error(mock_file_ingest):
    """Test no retry on 4xx client errors"""
    with patch('httpx.AsyncClient') as mock_client:
        # 400 error - should not retry
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Send webhook
        result = await send_webhook_with_retry(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest,
            retry=True
        )
        
        assert result is False
        assert mock_post.call_count == 1  # Should not retry


@pytest.mark.asyncio
async def test_exponential_backoff(mock_file_ingest):
    """Test exponential backoff delay between retries"""
    with patch('httpx.AsyncClient') as mock_client, \
         patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        
        # All attempts fail with 500
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Send webhook (will fail all retries)
        original_attempts = settings.WEBHOOK_RETRY_ATTEMPTS
        settings.WEBHOOK_RETRY_ATTEMPTS = 3
        
        try:
            result = await send_webhook_with_retry(
                event_type=WebhookEventType.FILE_PROCESSED,
                file_ingest=mock_file_ingest,
                retry=True
            )
            
            assert result is False
            assert mock_post.call_count == 3
            
            # Check exponential backoff delays
            # First retry: 5s, second retry: 10s
            assert mock_sleep.call_count == 2
            delays = [call.args[0] for call in mock_sleep.call_args_list]
            assert delays[0] == settings.WEBHOOK_RETRY_DELAY  # 5s
            assert delays[1] == settings.WEBHOOK_RETRY_DELAY * 2  # 10s
        finally:
            settings.WEBHOOK_RETRY_ATTEMPTS = original_attempts


# ============================================================================
# SIGNATURE TESTS
# ============================================================================

def test_generate_webhook_signature():
    """Test webhook signature generation"""
    payload = '{"event_type": "file.processed", "ingest_id": 123}'
    secret = "test-secret-key"
    
    signature = generate_webhook_signature(payload, secret)
    
    assert signature is not None
    assert len(signature) == 64  # SHA256 hex digest is 64 characters
    assert isinstance(signature, str)


def test_signature_consistency():
    """Test that same payload generates same signature"""
    payload = '{"event_type": "file.processed", "ingest_id": 123}'
    secret = "test-secret-key"
    
    sig1 = generate_webhook_signature(payload, secret)
    sig2 = generate_webhook_signature(payload, secret)
    
    assert sig1 == sig2


def test_signature_different_for_different_payloads():
    """Test that different payloads generate different signatures"""
    secret = "test-secret-key"
    
    sig1 = generate_webhook_signature('{"ingest_id": 123}', secret)
    sig2 = generate_webhook_signature('{"ingest_id": 456}', secret)
    
    assert sig1 != sig2


# ============================================================================
# FILTERING TESTS
# ============================================================================

def test_should_send_event_all_enabled():
    """Test event filtering when all events are enabled"""
    original_events = getattr(settings, 'WEBHOOK_ENABLED_EVENTS', None)
    settings.WEBHOOK_ENABLED_EVENTS = []  # Empty = all events
    
    try:
        assert should_send_event(WebhookEventType.FILE_PROCESSED) is True
        assert should_send_event(WebhookEventType.FILE_DELETED) is True
    finally:
        if original_events is not None:
            settings.WEBHOOK_ENABLED_EVENTS = original_events


def test_should_send_event_filtered():
    """Test event filtering when only specific events are enabled"""
    original_events = getattr(settings, 'WEBHOOK_ENABLED_EVENTS', None)
    settings.WEBHOOK_ENABLED_EVENTS = ["file.processed", "file.deleted"]
    
    try:
        assert should_send_event(WebhookEventType.FILE_PROCESSED) is True
        assert should_send_event(WebhookEventType.FILE_DELETED) is True
        assert should_send_event(WebhookEventType.FILE_INGESTED) is False
    finally:
        if original_events is not None:
            settings.WEBHOOK_ENABLED_EVENTS = original_events


# ============================================================================
# QUEUE TESTS
# ============================================================================

def test_webhook_queue_add():
    """Test adding webhook to queue"""
    queue = WebhookQueue(queue_file="data/test_webhook_queue.json")
    
    webhook_id = queue.add(
        event_type="file.processed",
        ingest_id=123,
        payload={"test": "data"},
        max_attempts=3
    )
    
    assert webhook_id is not None
    assert len(queue.queue) == 1
    assert queue.queue[0].event_type == "file.processed"
    assert queue.queue[0].ingest_id == 123
    
    # Cleanup
    Path("data/test_webhook_queue.json").unlink(missing_ok=True)


def test_webhook_queue_get_pending():
    """Test getting pending webhooks from queue"""
    queue = WebhookQueue(queue_file="data/test_webhook_queue.json")
    
    # Add some webhooks
    queue.add("file.processed", 123, {"test": "data1"})
    queue.add("file.deleted", 456, {"test": "data2"})
    
    pending = queue.get_pending()
    
    assert len(pending) == 2
    
    # Cleanup
    Path("data/test_webhook_queue.json").unlink(missing_ok=True)


def test_webhook_queue_update_status():
    """Test updating webhook status in queue"""
    queue = WebhookQueue(queue_file="data/test_webhook_queue.json")
    
    webhook_id = queue.add("file.processed", 123, {"test": "data"})
    
    queue.update_status(webhook_id, QueuedWebhookStatus.COMPLETED)
    
    assert queue.queue[0].status == QueuedWebhookStatus.COMPLETED
    assert queue.queue[0].attempts == 1
    
    # Cleanup
    Path("data/test_webhook_queue.json").unlink(missing_ok=True)


def test_webhook_queue_stats():
    """Test getting queue statistics"""
    queue = WebhookQueue(queue_file="data/test_webhook_queue.json")
    
    # Add webhooks with different statuses
    id1 = queue.add("file.processed", 123, {"test": "data1"})
    id2 = queue.add("file.deleted", 456, {"test": "data2"})
    
    queue.update_status(id1, QueuedWebhookStatus.COMPLETED)
    queue.update_status(id2, QueuedWebhookStatus.FAILED, "Test error")
    
    stats = queue.get_stats()
    
    assert stats["total"] == 2
    assert stats["completed"] == 1
    assert stats["failed"] == 1
    
    # Cleanup
    Path("data/test_webhook_queue.json").unlink(missing_ok=True)


# ============================================================================
# MONITORING TESTS
# ============================================================================

def test_webhook_monitor_record():
    """Test recording webhook metrics"""
    monitor = WebhookMonitor(metrics_file="data/test_webhook_metrics.json")
    
    monitor.record(
        event_type="file.processed",
        ingest_id=123,
        success=True,
        attempts=1,
        duration_ms=150.5,
        status_code=200
    )
    
    assert len(monitor.metrics) == 1
    assert monitor.metrics[0].event_type == "file.processed"
    assert monitor.metrics[0].success is True
    
    # Cleanup
    Path("data/test_webhook_metrics.json").unlink(missing_ok=True)


def test_webhook_monitor_stats():
    """Test getting webhook statistics"""
    monitor = WebhookMonitor(metrics_file="data/test_webhook_metrics.json")
    
    # Record some metrics
    monitor.record("file.processed", 123, True, 1, 100.0, 200)
    monitor.record("file.processed", 456, True, 1, 150.0, 200)
    monitor.record("file.deleted", 789, False, 3, 5000.0, 500)
    
    stats = monitor.get_stats(hours=24)
    
    assert stats["total"] == 3
    assert stats["successful"] == 2
    assert stats["failed"] == 1
    assert stats["success_rate"] == 66.67
    
    # Cleanup
    Path("data/test_webhook_metrics.json").unlink(missing_ok=True)


def test_webhook_monitor_health_status():
    """Test getting webhook health status"""
    monitor = WebhookMonitor(metrics_file="data/test_webhook_metrics.json")
    
    # Record successful metrics
    for i in range(10):
        monitor.record("file.processed", i, True, 1, 100.0, 200)
    
    health = monitor.get_health_status()
    
    assert health["status"] == "healthy"
    assert health["last_hour"]["success_rate"] == 100.0
    
    # Cleanup
    Path("data/test_webhook_metrics.json").unlink(missing_ok=True)

