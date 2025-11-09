"""
Module N - Webhook Tests
Tests for webhook notification functionality
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from module_n.webhooks import send_webhook, WebhookEventType
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


@pytest.mark.asyncio
async def test_send_webhook_success(mock_file_ingest):
    """Test successful webhook sending"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        # Send webhook
        result = await send_webhook(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest
        )
        
        assert result is True


@pytest.mark.asyncio
async def test_send_webhook_failure(mock_file_ingest):
    """Test webhook sending with HTTP error"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        # Send webhook
        result = await send_webhook(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest
        )
        
        assert result is False


@pytest.mark.asyncio
async def test_send_webhook_timeout(mock_file_ingest):
    """Test webhook sending with timeout"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock timeout exception
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.TimeoutException("Request timeout")
        )
        
        # Send webhook
        result = await send_webhook(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest
        )
        
        assert result is False


@pytest.mark.asyncio
async def test_send_webhook_request_error(mock_file_ingest):
    """Test webhook sending with request error"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock request exception
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.RequestError("Connection failed")
        )
        
        # Send webhook
        result = await send_webhook(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest
        )
        
        assert result is False


@pytest.mark.asyncio
async def test_send_webhook_no_url_configured(mock_file_ingest):
    """Test webhook sending when URL is not configured"""
    original_url = settings.LASER_OS_WEBHOOK_URL
    settings.LASER_OS_WEBHOOK_URL = ""
    
    try:
        # Send webhook
        result = await send_webhook(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest
        )
        
        assert result is False
    finally:
        settings.LASER_OS_WEBHOOK_URL = original_url


@pytest.mark.asyncio
async def test_send_webhook_with_additional_data(mock_file_ingest):
    """Test webhook sending with additional data"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Send webhook with additional data
        additional_data = {"hard_delete": True, "reason": "test"}
        result = await send_webhook(
            event_type=WebhookEventType.FILE_DELETED,
            file_ingest=mock_file_ingest,
            additional_data=additional_data
        )
        
        assert result is True
        
        # Verify additional data was included in the payload
        call_args = mock_post.call_args
        payload = call_args.kwargs['json']
        assert payload['file_data']['hard_delete'] is True
        assert payload['file_data']['reason'] == "test"


@pytest.mark.asyncio
async def test_webhook_event_types():
    """Test all webhook event types"""
    event_types = [
        WebhookEventType.FILE_INGESTED,
        WebhookEventType.FILE_PROCESSED,
        WebhookEventType.FILE_FAILED,
        WebhookEventType.FILE_RE_EXTRACTED,
        WebhookEventType.FILE_DELETED
    ]
    
    for event_type in event_types:
        assert event_type.value in [
            "file.ingested",
            "file.processed",
            "file.failed",
            "file.re_extracted",
            "file.deleted"
        ]


@pytest.mark.asyncio
async def test_webhook_payload_structure(mock_file_ingest):
    """Test webhook payload structure"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Send webhook
        await send_webhook(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest
        )
        
        # Verify payload structure
        call_args = mock_post.call_args
        payload = call_args.kwargs['json']
        
        assert 'event_type' in payload
        assert 'timestamp' in payload
        assert 'ingest_id' in payload
        assert 'file_data' in payload
        
        file_data = payload['file_data']
        assert file_data['ingest_id'] == 123
        assert file_data['original_filename'] == "test.dxf"
        assert file_data['client_code'] == "CL0001"
        assert file_data['project_code'] == "JB-2025-10-CL0001-001"
        assert file_data['material'] == "Mild Steel"
        assert file_data['thickness_mm'] == 5.0
        assert file_data['quantity'] == 10


@pytest.mark.asyncio
async def test_webhook_headers(mock_file_ingest):
    """Test webhook request headers"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Send webhook
        await send_webhook(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest
        )
        
        # Verify headers
        call_args = mock_post.call_args
        headers = call_args.kwargs['headers']
        assert headers['Content-Type'] == 'application/json'


@pytest.mark.asyncio
async def test_webhook_url_and_timeout(mock_file_ingest):
    """Test webhook uses correct URL and timeout"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Send webhook
        await send_webhook(
            event_type=WebhookEventType.FILE_PROCESSED,
            file_ingest=mock_file_ingest
        )
        
        # Verify URL
        call_args = mock_post.call_args
        url = call_args.args[0]
        assert url == settings.LASER_OS_WEBHOOK_URL
        
        # Verify timeout was set on client
        client_call_args = mock_client.call_args
        assert client_call_args.kwargs['timeout'] == settings.LASER_OS_TIMEOUT

