"""
Audit Logging Service for Compliance and Tracking

Logs all operations performed through the application for audit trail purposes.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json
import secrets
import logging
from sqlmodel import Session
from .db import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for creating and managing audit logs.
    """
    
    def __init__(self, tenant_id: str, user_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id or "system"
    
    def log_action(
        self,
        session: Session,
        action: str,
        target: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            session: Database session
            action: Action performed (e.g., "create_invoice", "update_contact")
            target: Target resource (e.g., "invoice:INV-001", "contact:12345")
            request_data: Request payload (will be JSON serialized)
            response_data: Response data (will be JSON serialized)
            status: Status of the action (preview, confirmed, success, failure)
            
        Returns:
            Created AuditLog object
        """
        try:
            audit_log = AuditLog(
                id=f"audit-{secrets.token_urlsafe(16)}",
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                action=action,
                target=target,
                request=json.dumps(request_data) if request_data else None,
                response=json.dumps(response_data) if response_data else None,
                status=status,
                created_at=datetime.utcnow()
            )
            
            session.add(audit_log)
            session.commit()
            session.refresh(audit_log)
            
            logger.info(f"Audit log created: {action} - {target} - {status}")
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            # Don't fail the main operation if audit logging fails
            session.rollback()
            raise
    
    def log_preview(
        self,
        session: Session,
        action: str,
        target: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Log a preview action (before confirmation).
        
        Args:
            session: Database session
            action: Action to be performed
            target: Target resource
            request_data: Request payload
            
        Returns:
            Created AuditLog object
        """
        return self.log_action(
            session=session,
            action=action,
            target=target,
            request_data=request_data,
            status="preview"
        )
    
    def log_confirmation(
        self,
        session: Session,
        audit_log_id: str,
        response_data: Optional[Dict[str, Any]] = None,
        status: str = "confirmed"
    ) -> Optional[AuditLog]:
        """
        Update a preview audit log to confirmed status.
        
        Args:
            session: Database session
            audit_log_id: ID of the audit log to update
            response_data: Response data from the operation
            status: New status (confirmed, success, failure)
            
        Returns:
            Updated AuditLog object or None if not found
        """
        try:
            audit_log = session.get(AuditLog, audit_log_id)
            
            if not audit_log:
                logger.warning(f"Audit log not found: {audit_log_id}")
                return None
            
            audit_log.status = status
            if response_data:
                audit_log.response = json.dumps(response_data)
            
            session.add(audit_log)
            session.commit()
            session.refresh(audit_log)
            
            logger.info(f"Audit log updated: {audit_log_id} - {status}")
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to update audit log: {str(e)}")
            session.rollback()
            raise
    
    def log_api_call(
        self,
        session: Session,
        endpoint: str,
        method: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        status_code: int = 200
    ) -> AuditLog:
        """
        Log an API call to Sage.
        
        Args:
            session: Database session
            endpoint: API endpoint called
            method: HTTP method (GET, POST, PUT, DELETE)
            request_data: Request payload
            response_data: Response data
            status_code: HTTP status code
            
        Returns:
            Created AuditLog object
        """
        status = "success" if 200 <= status_code < 300 else "failure"
        
        return self.log_action(
            session=session,
            action=f"api_call:{method}",
            target=endpoint,
            request_data=request_data,
            response_data=response_data,
            status=status
        )
    
    def log_oauth_event(
        self,
        session: Session,
        event: str,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ) -> AuditLog:
        """
        Log OAuth-related events.
        
        Args:
            session: Database session
            event: OAuth event (e.g., "oauth_start", "oauth_callback", "token_refresh")
            details: Event details
            status: Event status
            
        Returns:
            Created AuditLog object
        """
        return self.log_action(
            session=session,
            action=f"oauth:{event}",
            request_data=details,
            status=status
        )
    
    def log_business_operation(
        self,
        session: Session,
        operation: str,
        document_type: str,
        document_id: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ) -> AuditLog:
        """
        Log business document operations (create, update, delete, etc.).
        
        Args:
            session: Database session
            operation: Operation performed (create, update, delete, release, void, etc.)
            document_type: Type of document (invoice, quote, contact, etc.)
            document_id: ID of the document
            request_data: Request payload
            response_data: Response data
            status: Operation status
            
        Returns:
            Created AuditLog object
        """
        target = f"{document_type}:{document_id}" if document_id else document_type
        
        return self.log_action(
            session=session,
            action=f"{operation}_{document_type}",
            target=target,
            request_data=request_data,
            response_data=response_data,
            status=status
        )


def get_audit_service(tenant_id: str, user_id: Optional[str] = None) -> AuditService:
    """
    Factory function to create AuditService instance.
    
    Args:
        tenant_id: Tenant identifier
        user_id: User identifier (optional)
        
    Returns:
        AuditService instance
    """
    return AuditService(tenant_id, user_id)

