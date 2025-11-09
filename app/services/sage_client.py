"""
Sage Business Cloud Accounting API Client

This service handles all interactions with the Sage API including:
- Token management and refresh
- API requests with proper headers
- Error handling and retry logic
- South African localization defaults
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from flask import current_app
from app import db
from app.models import SageConnection, SageBusiness, SageAuditLog


class SageAPIClient:
    """
    Client for interacting with Sage Business Cloud Accounting API v3.1
    
    Base URL: https://api.accounting.sage.com/v3.1
    Documentation: https://developer.sage.com/accounting/reference/
    """
    
    BASE_URL = 'https://api.accounting.sage.com/v3.1'
    TOKEN_URL = 'https://oauth.accounting.sage.com/token'
    
    # South African defaults
    DEFAULT_CURRENCY = 'ZAR'
    DEFAULT_TAX_RATE_NAME = 'ZA_STANDARD'  # 15% VAT
    DEFAULT_PAYMENT_TERMS_DAYS = 30
    
    def __init__(self, connection: SageConnection, business: Optional[SageBusiness] = None):
        """
        Initialize Sage API client.
        
        Args:
            connection: SageConnection instance with OAuth tokens
            business: Optional SageBusiness instance for X-Business header
        """
        self.connection = connection
        self.business = business
        self._ensure_valid_token()
    
    def _ensure_valid_token(self):
        """Ensure access token is valid, refresh if needed."""
        if self.connection.is_token_expired():
            self._refresh_token()
    
    def _refresh_token(self):
        """
        Refresh the OAuth access token using the refresh token.
        
        Sage tokens expire after 5 minutes, so we refresh proactively.
        """
        try:
            # Get OAuth credentials from config
            client_id = current_app.config.get('SAGE_CLIENT_ID')
            client_secret = current_app.config.get('SAGE_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                raise ValueError("Sage OAuth credentials not configured")
            
            # Request new token
            response = requests.post(
                self.TOKEN_URL,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.connection.refresh_token,
                    'client_id': client_id,
                    'client_secret': client_secret
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update connection with new tokens
                self.connection.access_token = token_data['access_token']
                self.connection.refresh_token = token_data.get('refresh_token', self.connection.refresh_token)
                self.connection.expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
                self.connection.updated_at = datetime.utcnow()
                
                db.session.commit()
                
                current_app.logger.info(f"Refreshed Sage token for user {self.connection.user_id}")
            else:
                current_app.logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                raise Exception(f"Token refresh failed: {response.status_code}")
                
        except Exception as e:
            current_app.logger.error(f"Error refreshing Sage token: {str(e)}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for Sage API requests.
        
        Returns:
            Dictionary of headers including Authorization and X-Business
        """
        headers = {
            'Authorization': f'Bearer {self.connection.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add X-Business header if business is selected
        if self.business:
            headers['X-Business'] = self.business.sage_business_id
        
        return headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        audit_log: bool = True
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Sage API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/sales_invoices')
            params: Query parameters
            data: Request body data
            audit_log: Whether to create an audit log entry
            
        Returns:
            Response data as dictionary
        """
        self._ensure_valid_token()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            
            # Log the request if audit logging is enabled
            if audit_log and method in ['POST', 'PUT', 'DELETE']:
                self._create_audit_log(
                    operation_type=method.lower(),
                    endpoint=endpoint,
                    request_data=data,
                    response_status=response.status_code,
                    response_data=response.json() if response.ok else None,
                    error_message=response.text if not response.ok else None
                )
            
            # Raise exception for error status codes
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Sage API request failed: {method} {endpoint} - {str(e)}")
            raise
    
    def _create_audit_log(
        self,
        operation_type: str,
        endpoint: str,
        request_data: Optional[Dict] = None,
        response_status: int = 0,
        response_data: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """Create an audit log entry for the operation."""
        try:
            # Determine resource type from endpoint
            resource_type = endpoint.strip('/').split('/')[0] if endpoint else 'unknown'
            
            # Determine status
            if error_message:
                status = 'failed'
            elif response_status >= 200 and response_status < 300:
                status = 'success'
            else:
                status = 'failed'
            
            # Extract resource ID if available
            resource_id = None
            if response_data and isinstance(response_data, dict):
                resource_id = response_data.get('id')
            
            # Create audit log
            audit_log = SageAuditLog(
                connection_id=self.connection.id,
                user_id=self.connection.user_id,
                operation_type=operation_type,
                resource_type=resource_type,
                resource_id=resource_id,
                status=status,
                error_message=error_message
            )
            
            if request_data:
                audit_log.set_request_data(request_data)
            if response_data:
                audit_log.set_response_data(response_data)
            
            db.session.add(audit_log)
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Failed to create audit log: {str(e)}")
            # Don't raise - audit logging failure shouldn't break the main operation
    
    # ========================================================================
    # Business Management
    # ========================================================================
    
    def get_businesses(self) -> List[Dict[str, Any]]:
        """
        Get list of businesses the user has access to.
        
        Returns:
            List of business dictionaries
        """
        response = self._make_request('GET', '/businesses', audit_log=False)
        return response.get('$items', [])
    
    # ========================================================================
    # Sales Invoices
    # ========================================================================
    
    def get_sales_invoices(
        self,
        page: int = 1,
        items_per_page: int = 20,
        updated_since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get sales invoices from Sage.
        
        Args:
            page: Page number (1-indexed)
            items_per_page: Number of items per page
            updated_since: Only get invoices updated after this timestamp
            
        Returns:
            Dictionary with $items and pagination info
        """
        params = {
            'page': page,
            'items_per_page': items_per_page
        }
        
        if updated_since:
            params['updated_or_created_since'] = updated_since.isoformat()
        
        return self._make_request('GET', '/sales_invoices', params=params, audit_log=False)
    
    def get_sales_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get a specific sales invoice by ID."""
        return self._make_request('GET', f'/sales_invoices/{invoice_id}', audit_log=False)
    
    def create_sales_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new sales invoice in Sage.
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Created invoice data
        """
        return self._make_request('POST', '/sales_invoices', data=invoice_data)
    
    # ========================================================================
    # Sales Quotes
    # ========================================================================
    
    def get_sales_quotes(
        self,
        page: int = 1,
        items_per_page: int = 20,
        updated_since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get sales quotes from Sage."""
        params = {
            'page': page,
            'items_per_page': items_per_page
        }
        
        if updated_since:
            params['updated_or_created_since'] = updated_since.isoformat()
        
        return self._make_request('GET', '/sales_quotes', params=params, audit_log=False)
    
    def create_sales_quote(self, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new sales quote in Sage."""
        return self._make_request('POST', '/sales_quotes', data=quote_data)
    
    # ========================================================================
    # Contacts
    # ========================================================================
    
    def get_contacts(
        self,
        page: int = 1,
        items_per_page: int = 20,
        contact_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get contacts from Sage.
        
        Args:
            page: Page number
            items_per_page: Items per page
            contact_type: Filter by type ('CUSTOMER', 'SUPPLIER', or None for all)
        """
        params = {
            'page': page,
            'items_per_page': items_per_page
        }
        
        if contact_type:
            params['contact_type'] = contact_type
        
        return self._make_request('GET', '/contacts', params=params, audit_log=False)
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact in Sage."""
        return self._make_request('POST', '/contacts', data=contact_data)

