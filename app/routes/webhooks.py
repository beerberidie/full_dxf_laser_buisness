"""
Laser OS - Webhook Routes
Receives webhook notifications from Module N and other external services
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from app import db
from app.models import Project, DesignFile, Client
from app.services.activity_logger import log_activity
from datetime import datetime
import logging
import hmac
import hashlib
import json
import os

bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')
logger = logging.getLogger(__name__)


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature using HMAC-SHA256.

    Args:
        payload: Raw request payload bytes
        signature: Signature from X-Webhook-Signature header
        secret: Secret key for verification

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not secret:
        return False

    # Extract signature (format: "sha256=<hex_digest>")
    if signature.startswith('sha256='):
        signature = signature[7:]

    # Calculate expected signature
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(signature, expected)


@bp.route('/module-n/event', methods=['POST'])
def module_n_event():
    """
    Receive webhook events from Module N.
    
    Event Types:
        - file.ingested: File uploaded and validated
        - file.processed: File parsed and metadata extracted
        - file.failed: File processing failed
        - file.re_extracted: File re-extracted
        - file.deleted: File deleted
    
    Payload:
        {
            "event_type": "file.processed",
            "timestamp": "2025-10-21T10:30:00",
            "ingest_id": 123,
            "file_data": {
                "ingest_id": 123,
                "original_filename": "bracket.dxf",
                "stored_filename": "CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
                "file_path": "CL0001/JB-2025-10-CL0001-001/...",
                "file_type": "dxf",
                "file_size": 12345,
                "status": "completed",
                "confidence_score": 0.95,
                "client_code": "CL0001",
                "project_code": "JB-2025-10-CL0001-001",
                "part_name": "Bracket",
                "material": "Mild Steel",
                "thickness_mm": 5.0,
                "quantity": 10,
                "version": 1,
                "created_at": "2025-10-21T10:29:00",
                "processed_at": "2025-10-21T10:30:00"
            }
        }
    """
    try:
        # Verify webhook signature if secret is configured
        webhook_secret = os.getenv('WEBHOOK_SECRET', '')
        if webhook_secret:
            signature = request.headers.get('X-Webhook-Signature', '')
            payload = request.get_data()

            if not verify_webhook_signature(payload, signature, webhook_secret):
                logger.error("Webhook signature verification failed")
                return jsonify({'success': False, 'error': 'Invalid signature'}), 401

            logger.debug("Webhook signature verified successfully")

        # Get webhook payload
        data = request.get_json()

        if not data:
            logger.error("Webhook received with no data")
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        event_type = data.get('event_type')
        file_data = data.get('file_data', {})
        ingest_id = data.get('ingest_id')
        
        logger.info(f"Webhook received: {event_type} for ingest_id={ingest_id}")
        logger.debug(f"Webhook data: {data}")
        
        # Handle different event types
        if event_type == 'file.processed':
            return handle_file_processed(file_data)
        elif event_type == 'file.ingested':
            return handle_file_ingested(file_data)
        elif event_type == 'file.failed':
            return handle_file_failed(file_data)
        elif event_type == 'file.re_extracted':
            return handle_file_re_extracted(file_data)
        elif event_type == 'file.deleted':
            return handle_file_deleted(file_data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return jsonify({'success': True, 'message': 'Event type not handled'}), 200
            
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def handle_file_processed(file_data: dict) -> tuple:
    """
    Handle file.processed event.
    Creates or updates DesignFile record in Laser OS.
    
    Args:
        file_data: File data from webhook
        
    Returns:
        JSON response tuple
    """
    try:
        project_code = file_data.get('project_code')
        client_code = file_data.get('client_code')
        
        # Find project by project_code
        project = None
        if project_code:
            project = Project.query.filter_by(project_code=project_code).first()
        
        # If no project found and we have client_code, try to find or create
        if not project and client_code:
            client = Client.query.filter_by(client_code=client_code).first()
            if client:
                logger.info(f"Found client {client.name} for file, but no matching project")
        
        # Create or update DesignFile record
        if project:
            # Check if file already exists
            design_file = DesignFile.query.filter_by(
                project_id=project.id,
                filename=file_data.get('stored_filename')
            ).first()
            
            if design_file:
                # Update existing file
                design_file.file_type = file_data.get('file_type', 'unknown')
                design_file.file_size = file_data.get('file_size', 0)
                design_file.file_path = file_data.get('file_path', '')
                design_file.updated_at = datetime.utcnow()
                logger.info(f"Updated existing DesignFile {design_file.id} for project {project.project_code}")
            else:
                # Create new file record
                design_file = DesignFile(
                    project_id=project.id,
                    filename=file_data.get('stored_filename', file_data.get('original_filename')),
                    original_filename=file_data.get('original_filename'),
                    file_type=file_data.get('file_type', 'unknown'),
                    file_size=file_data.get('file_size', 0),
                    file_path=file_data.get('file_path', ''),
                    upload_date=datetime.utcnow(),
                    uploaded_by_id=None,  # System upload
                    notes=f"Processed by Module N (ingest_id: {file_data.get('ingest_id')})"
                )
                db.session.add(design_file)
                logger.info(f"Created new DesignFile for project {project.project_code}")
            
            db.session.commit()
            
            # Log activity
            log_activity(
                'FILE',
                design_file.id,
                'PROCESSED',
                {
                    'filename': design_file.filename,
                    'project': project.project_code,
                    'material': file_data.get('material'),
                    'thickness': file_data.get('thickness_mm'),
                    'quantity': file_data.get('quantity'),
                    'confidence': file_data.get('confidence_score')
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'File processed successfully',
                'design_file_id': design_file.id,
                'project_id': project.id
            }), 200
        else:
            logger.warning(f"No project found for project_code={project_code}")
            return jsonify({
                'success': True,
                'message': 'File processed but no matching project found',
                'warning': f'Project {project_code} not found in Laser OS'
            }), 200
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error handling file.processed event: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def handle_file_ingested(file_data: dict) -> tuple:
    """
    Handle file.ingested event.
    File has been uploaded and validated but not yet processed.
    
    Args:
        file_data: File data from webhook
        
    Returns:
        JSON response tuple
    """
    logger.info(f"File ingested: {file_data.get('original_filename')}")
    return jsonify({
        'success': True,
        'message': 'File ingestion acknowledged'
    }), 200


def handle_file_failed(file_data: dict) -> tuple:
    """
    Handle file.failed event.
    File processing failed.
    
    Args:
        file_data: File data from webhook
        
    Returns:
        JSON response tuple
    """
    logger.error(f"File processing failed: {file_data.get('original_filename')}")
    
    # Could send notification to admin or log to database
    # For now, just acknowledge
    
    return jsonify({
        'success': True,
        'message': 'File failure acknowledged'
    }), 200


def handle_file_re_extracted(file_data: dict) -> tuple:
    """
    Handle file.re_extracted event.
    File has been re-extracted with updated metadata.
    
    Args:
        file_data: File data from webhook
        
    Returns:
        JSON response tuple
    """
    logger.info(f"File re-extracted: {file_data.get('original_filename')}")
    
    # Update existing DesignFile if found
    return handle_file_processed(file_data)


def handle_file_deleted(file_data: dict) -> tuple:
    """
    Handle file.deleted event.
    File has been deleted from Module N.
    
    Args:
        file_data: File data from webhook
        
    Returns:
        JSON response tuple
    """
    try:
        stored_filename = file_data.get('stored_filename')
        
        # Find and mark file as deleted (soft delete)
        design_file = DesignFile.query.filter_by(filename=stored_filename).first()
        
        if design_file:
            design_file.is_deleted = True
            design_file.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Marked DesignFile {design_file.id} as deleted")
            
            return jsonify({
                'success': True,
                'message': 'File deletion acknowledged',
                'design_file_id': design_file.id
            }), 200
        else:
            logger.warning(f"File not found for deletion: {stored_filename}")
            return jsonify({
                'success': True,
                'message': 'File not found in Laser OS'
            }), 200
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error handling file.deleted event: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/module-n/health', methods=['GET'])
def module_n_health():
    """Health check endpoint for Module N webhook receiver"""
    return jsonify({
        'status': 'healthy',
        'service': 'laser-os-webhooks',
        'endpoint': '/webhooks/module-n/event'
    }), 200

