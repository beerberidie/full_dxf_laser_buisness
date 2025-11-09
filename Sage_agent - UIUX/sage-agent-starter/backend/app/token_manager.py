"""
Token Management Service for Sage Business Cloud Accounting OAuth 2.0

Handles automatic token refresh since access tokens expire in 5 minutes.
"""

from datetime import datetime, timedelta
from typing import Optional
import httpx
import logging
from sqlmodel import Session, select
from .db import Connection
from .settings import get_settings

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manages OAuth token lifecycle including automatic refresh.
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.settings = get_settings()
    
    def _get_connection(self, session: Session) -> Optional[Connection]:
        """Get the connection for this tenant."""
        return session.exec(
            select(Connection).where(
                Connection.tenant_id == self.tenant_id,
                Connection.provider == "sbca"
            )
        ).first()
    
    def is_token_expired(self, conn: Connection) -> bool:
        """
        Check if the access token is expired or will expire soon.
        Add 30 second buffer to refresh before actual expiration.
        """
        if not conn.expires_at:
            return True
        
        # Refresh if token expires in less than 30 seconds
        buffer = timedelta(seconds=30)
        return datetime.utcnow() + buffer >= conn.expires_at
    
    async def refresh_token(self, session: Session, conn: Connection) -> Connection:
        """
        Refresh the access token using the refresh token.
        
        Args:
            session: Database session
            conn: Connection object with refresh_token
            
        Returns:
            Updated Connection object with new tokens
            
        Raises:
            HTTPException: If refresh fails
        """
        if not conn.refresh_token:
            raise ValueError("No refresh token available")
        
        token_url = "https://oauth.accounting.sage.com/token"
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": conn.refresh_token,
            "client_id": self.settings.sage_client_id,
            "client_secret": self.settings.sage_client_secret,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(token_url, data=data)
                resp.raise_for_status()
                tok = resp.json()
            
            # Update connection with new tokens
            conn.access_token = tok.get("access_token")
            conn.refresh_token = tok.get("refresh_token", conn.refresh_token)  # Keep old if not provided
            conn.expires_at = datetime.utcnow() + timedelta(seconds=tok.get("expires_in", 300))
            
            session.add(conn)
            session.commit()
            session.refresh(conn)
            
            logger.info(f"Token refreshed successfully for tenant: {self.tenant_id}")
            
            return conn
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Token refresh failed: {e.response.text}")
            # If refresh fails, mark connection as inactive
            conn.status = "token_refresh_failed"
            session.add(conn)
            session.commit()
            raise ValueError(f"Token refresh failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise ValueError(f"Token refresh error: {str(e)}")
    
    async def get_valid_token(self, session: Session) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            session: Database session
            
        Returns:
            Valid access token string
            
        Raises:
            ValueError: If no connection exists or token refresh fails
        """
        conn = self._get_connection(session)
        
        if not conn:
            raise ValueError("No Sage connection found. Please authenticate first.")
        
        if not conn.access_token:
            raise ValueError("No access token available. Please re-authenticate.")
        
        # Check if token needs refresh
        if self.is_token_expired(conn):
            logger.info(f"Token expired for tenant {self.tenant_id}, refreshing...")
            conn = await self.refresh_token(session, conn)
        
        return conn.access_token
    
    async def get_connection_with_valid_token(self, session: Session) -> Connection:
        """
        Get connection object with a valid access token.
        Automatically refreshes token if needed.
        
        Args:
            session: Database session
            
        Returns:
            Connection object with valid access token
            
        Raises:
            ValueError: If no connection exists or token refresh fails
        """
        conn = self._get_connection(session)
        
        if not conn:
            raise ValueError("No Sage connection found. Please authenticate first.")
        
        if not conn.access_token:
            raise ValueError("No access token available. Please re-authenticate.")
        
        # Check if token needs refresh
        if self.is_token_expired(conn):
            logger.info(f"Token expired for tenant {self.tenant_id}, refreshing...")
            conn = await self.refresh_token(session, conn)
        
        return conn


def get_token_manager(tenant_id: str) -> TokenManager:
    """
    Factory function to create TokenManager instance.
    
    Args:
        tenant_id: Tenant identifier
        
    Returns:
        TokenManager instance
    """
    return TokenManager(tenant_id)

