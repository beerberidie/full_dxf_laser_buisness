"""
Sage OAuth 2.0 Authentication Service

This service handles the OAuth 2.0 flow for Sage Business Cloud Accounting:
1. Generate authorization URL
2. Exchange authorization code for tokens
3. Store tokens in database
4. Manage business selection
"""

import requests
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode
from flask import current_app, session
from app import db
from app.models import SageConnection, SageBusiness, User


class SageAuthService:
    """
    Service for handling Sage OAuth 2.0 authentication flow.
    
    OAuth URLs:
    - Authorize: https://www.sageone.com/oauth2/auth/central?filter=apiv3.1
    - Token: https://oauth.accounting.sage.com/token
    """
    
    AUTHORIZE_URL = 'https://www.sageone.com/oauth2/auth/central'
    TOKEN_URL = 'https://oauth.accounting.sage.com/token'
    
    @staticmethod
    def get_authorization_url(redirect_uri: str) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL for user to authenticate with Sage.
        
        Args:
            redirect_uri: Callback URL after authorization
            
        Returns:
            Tuple of (authorization_url, state) where state is used for CSRF protection
        """
        # Get OAuth credentials from config
        client_id = current_app.config.get('SAGE_CLIENT_ID')
        
        if not client_id:
            raise ValueError("SAGE_CLIENT_ID not configured")
        
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in session for verification
        session['sage_oauth_state'] = state
        
        # Build authorization URL
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'full_access',  # Request full access to Sage API
            'state': state,
            'filter': 'apiv3.1'  # Filter for API v3.1
        }
        
        auth_url = f"{SageAuthService.AUTHORIZE_URL}?{urlencode(params)}"
        
        return auth_url, state
    
    @staticmethod
    def verify_state(state: str) -> bool:
        """
        Verify OAuth state parameter to prevent CSRF attacks.
        
        Args:
            state: State parameter from OAuth callback
            
        Returns:
            True if state is valid, False otherwise
        """
        stored_state = session.get('sage_oauth_state')
        
        if not stored_state:
            return False
        
        # Clear state from session after verification
        session.pop('sage_oauth_state', None)
        
        return state == stored_state
    
    @staticmethod
    def exchange_code_for_tokens(code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Same redirect URI used in authorization request
            
        Returns:
            Dictionary containing token data
        """
        # Get OAuth credentials from config
        client_id = current_app.config.get('SAGE_CLIENT_ID')
        client_secret = current_app.config.get('SAGE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("Sage OAuth credentials not configured")
        
        # Request tokens
        response = requests.post(
            SageAuthService.TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': client_id,
                'client_secret': client_secret
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code != 200:
            current_app.logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Token exchange failed: {response.status_code}")
        
        return response.json()
    
    @staticmethod
    def create_or_update_connection(user: User, token_data: Dict[str, Any]) -> SageConnection:
        """
        Create or update Sage connection for a user.
        
        Args:
            user: User instance
            token_data: Token data from OAuth exchange
            
        Returns:
            SageConnection instance
        """
        # Check if connection already exists
        connection = SageConnection.query.filter_by(user_id=user.id).first()
        
        if connection:
            # Update existing connection
            connection.access_token = token_data['access_token']
            connection.refresh_token = token_data['refresh_token']
            connection.token_type = token_data.get('token_type', 'Bearer')
            connection.expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
            connection.scope = token_data.get('scope')
            connection.is_active = True
            connection.updated_at = datetime.utcnow()
        else:
            # Create new connection
            connection = SageConnection(
                user_id=user.id,
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                token_type=token_data.get('token_type', 'Bearer'),
                expires_at=datetime.utcnow() + timedelta(seconds=token_data['expires_in']),
                scope=token_data.get('scope'),
                is_active=True
            )
            db.session.add(connection)
        
        db.session.commit()
        
        current_app.logger.info(f"Created/updated Sage connection for user {user.id}")
        
        return connection
    
    @staticmethod
    def load_businesses(connection: SageConnection) -> list:
        """
        Load businesses from Sage API and store in database.
        
        Args:
            connection: SageConnection instance
            
        Returns:
            List of SageBusiness instances
        """
        from app.services.sage_client import SageAPIClient
        
        # Create API client (without business context)
        client = SageAPIClient(connection)
        
        # Get businesses from Sage
        businesses_data = client.get_businesses()
        
        # Store businesses in database
        businesses = []
        for business_data in businesses_data:
            # Check if business already exists
            business = SageBusiness.query.filter_by(
                connection_id=connection.id,
                sage_business_id=business_data['id']
            ).first()
            
            if business:
                # Update existing business
                business.name = business_data.get('name')
                business.displayed_as = business_data.get('displayed_as')
                business.updated_at = datetime.utcnow()
            else:
                # Create new business
                business = SageBusiness(
                    connection_id=connection.id,
                    sage_business_id=business_data['id'],
                    name=business_data.get('name'),
                    displayed_as=business_data.get('displayed_as'),
                    is_selected=False
                )
                db.session.add(business)
            
            # Store additional metadata
            business.set_metadata(business_data)
            
            businesses.append(business)
        
        db.session.commit()
        
        current_app.logger.info(f"Loaded {len(businesses)} businesses for connection {connection.id}")
        
        return businesses
    
    @staticmethod
    def select_business(connection: SageConnection, business_id: int) -> SageBusiness:
        """
        Select a business for the user to work with.
        
        Args:
            connection: SageConnection instance
            business_id: ID of the business to select (local database ID)
            
        Returns:
            Selected SageBusiness instance
        """
        # Get the business
        business = SageBusiness.query.filter_by(
            id=business_id,
            connection_id=connection.id
        ).first()
        
        if not business:
            raise ValueError(f"Business {business_id} not found for connection {connection.id}")
        
        # Deselect all other businesses for this connection
        SageBusiness.query.filter_by(connection_id=connection.id).update({'is_selected': False})
        
        # Select this business
        business.is_selected = True
        business.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        current_app.logger.info(f"Selected business {business_id} for connection {connection.id}")
        
        return business
    
    @staticmethod
    def get_selected_business(connection: SageConnection) -> Optional[SageBusiness]:
        """
        Get the currently selected business for a connection.
        
        Args:
            connection: SageConnection instance
            
        Returns:
            Selected SageBusiness instance or None
        """
        return SageBusiness.query.filter_by(
            connection_id=connection.id,
            is_selected=True
        ).first()
    
    @staticmethod
    def disconnect(user: User) -> bool:
        """
        Disconnect Sage integration for a user.
        
        Args:
            user: User instance
            
        Returns:
            True if disconnected successfully
        """
        connection = SageConnection.query.filter_by(user_id=user.id).first()
        
        if connection:
            connection.is_active = False
            connection.updated_at = datetime.utcnow()
            db.session.commit()
            
            current_app.logger.info(f"Disconnected Sage for user {user.id}")
            return True
        
        return False
    
    @staticmethod
    def get_connection_status(user: User) -> Dict[str, Any]:
        """
        Get Sage connection status for a user.
        
        Args:
            user: User instance
            
        Returns:
            Dictionary with connection status information
        """
        connection = SageConnection.query.filter_by(user_id=user.id).first()
        
        if not connection or not connection.is_active:
            return {
                'connected': False,
                'status': 'not_connected'
            }
        
        # Check if token is expired
        if connection.is_token_expired():
            return {
                'connected': True,
                'status': 'token_expired',
                'connection_id': connection.id
            }
        
        # Check if business is selected
        selected_business = SageAuthService.get_selected_business(connection)
        
        if not selected_business:
            return {
                'connected': True,
                'status': 'pending_business_selection',
                'connection_id': connection.id
            }
        
        return {
            'connected': True,
            'status': 'active',
            'connection_id': connection.id,
            'business_id': selected_business.id,
            'business_name': selected_business.displayed_as or selected_business.name
        }

