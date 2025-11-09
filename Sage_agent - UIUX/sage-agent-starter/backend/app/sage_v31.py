from fastapi import HTTPException
from typing import Any, Dict, Optional
import httpx
from .db import Connection, get_session
from sqlmodel import select
from datetime import datetime, timedelta
from .settings import get_settings
from .token_manager import get_token_manager
import logging

logger = logging.getLogger(__name__)


class SageV31Client:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.settings = get_settings()
        self.token_manager = get_token_manager(tenant_id)

    async def _request(self, method: str, path: str, *, params: Dict[str, Any] | None=None, json: Dict[str, Any] | None=None, headers: Dict[str,str] | None=None):
        """
        Make an authenticated request to Sage API.
        Automatically handles token refresh and X-Business header.
        """
        base = self.settings.sage_base_url.rstrip("/")
        url = f"{base}{path}"

        async with httpx.AsyncClient(timeout=60) as client, get_session() as session:
            # Get connection with valid token (auto-refreshes if needed)
            try:
                conn = await self.token_manager.get_connection_with_valid_token(session)
            except ValueError as e:
                raise HTTPException(status_code=401, detail=str(e))

            # Ensure business_id is set
            if not conn.business_id:
                raise HTTPException(
                    status_code=400,
                    detail="Business not selected. Please select a business first."
                )

            # Build headers with required Sage API headers
            h = {
                "Authorization": f"Bearer {conn.access_token}",
                "X-Business": conn.business_id,  # REQUIRED for all Sage API requests
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            if headers:
                h.update(headers)

            logger.debug(f"Sage API Request: {method} {url}")

            try:
                resp = await client.request(method, url, params=params, json=json, headers=h)

                # Handle 401 - token might have expired between check and request
                if resp.status_code == 401:
                    logger.warning("Received 401, attempting token refresh...")
                    conn = await self.token_manager.refresh_token(session, conn)
                    h["Authorization"] = f"Bearer {conn.access_token}"

                    # Retry request with new token
                    resp = await client.request(method, url, params=params, json=json, headers=h)

                if resp.status_code >= 400:
                    logger.error(f"Sage API Error {resp.status_code}: {resp.text}")
                    raise HTTPException(status_code=resp.status_code, detail=resp.text)

                return resp.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error: {e}")
                raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
            except Exception as e:
                logger.error(f"Request Error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    # ============================================================================
    # QUOTES METHODS
    # ============================================================================

    async def list_sales_quotes(self, updated_since: Optional[str]=None, items_per_page: int=50):
        """List all sales quotes"""
        params = {"items_per_page": items_per_page}
        if updated_since:
            params["updated_or_created_since"] = updated_since
        return await self._request("GET", "/sales_quotes", params=params)

    async def get_sales_quote(self, quote_id: str):
        """Get a specific sales quote by ID"""
        return await self._request("GET", f"/sales_quotes/{quote_id}")

    async def create_sales_quote(self, payload: Dict[str, Any]):
        """Create a new sales quote"""
        return await self._request("POST", "/sales_quotes", json=payload)

    async def update_sales_quote(self, quote_id: str, payload: Dict[str, Any]):
        """Update an existing sales quote"""
        return await self._request("PUT", f"/sales_quotes/{quote_id}", json=payload)

    async def delete_sales_quote(self, quote_id: str):
        """Delete a sales quote"""
        return await self._request("DELETE", f"/sales_quotes/{quote_id}")

    # ============================================================================
    # ESTIMATES METHODS
    # ============================================================================

    async def list_sales_estimates(self, updated_since: Optional[str]=None, items_per_page: int=50):
        """List all sales estimates"""
        params = {"items_per_page": items_per_page}
        if updated_since:
            params["updated_or_created_since"] = updated_since
        return await self._request("GET", "/sales_estimates", params=params)

    async def get_sales_estimate(self, estimate_id: str):
        """Get a specific sales estimate by ID"""
        return await self._request("GET", f"/sales_estimates/{estimate_id}")

    async def create_sales_estimate(self, payload: Dict[str, Any]):
        """Create a new sales estimate"""
        return await self._request("POST", "/sales_estimates", json=payload)

    async def update_sales_estimate(self, estimate_id: str, payload: Dict[str, Any]):
        """Update an existing sales estimate"""
        return await self._request("PUT", f"/sales_estimates/{estimate_id}", json=payload)

    async def delete_sales_estimate(self, estimate_id: str):
        """Delete a sales estimate"""
        return await self._request("DELETE", f"/sales_estimates/{estimate_id}")

    # ============================================================================
    # INVOICES METHODS
    # ============================================================================

    async def list_sales_invoices(self, updated_since: Optional[str]=None, items_per_page: int=50):
        """List all sales invoices"""
        params = {"items_per_page": items_per_page}
        if updated_since:
            params["updated_or_created_since"] = updated_since
        return await self._request("GET", "/sales_invoices", params=params)

    async def get_sales_invoice(self, invoice_id: str):
        """Get a specific sales invoice by ID"""
        return await self._request("GET", f"/sales_invoices/{invoice_id}")

    async def create_sales_invoice(self, payload: Dict[str, Any]):
        """Create a new sales invoice"""
        return await self._request("POST", "/sales_invoices", json=payload)

    async def update_sales_invoice(self, invoice_id: str, payload: Dict[str, Any]):
        """Update an existing sales invoice"""
        return await self._request("PUT", f"/sales_invoices/{invoice_id}", json=payload)

    async def delete_sales_invoice(self, invoice_id: str):
        """Delete a sales invoice"""
        return await self._request("DELETE", f"/sales_invoices/{invoice_id}")

    async def release_sales_invoice(self, invoice_id: str):
        """Release (finalize) a sales invoice"""
        return await self._request("POST", f"/sales_invoices/{invoice_id}/release")

    # ============================================================================
    # CREDIT NOTES METHODS
    # ============================================================================

    async def list_sales_credit_notes(self, updated_since: Optional[str]=None, items_per_page: int=50):
        """List all sales credit notes"""
        params = {"items_per_page": items_per_page}
        if updated_since:
            params["updated_or_created_since"] = updated_since
        return await self._request("GET", "/sales_credit_notes", params=params)

    async def get_sales_credit_note(self, credit_note_id: str):
        """Get a specific sales credit note by ID"""
        return await self._request("GET", f"/sales_credit_notes/{credit_note_id}")

    async def create_sales_credit_note(self, payload: Dict[str, Any]):
        """Create a new sales credit note"""
        return await self._request("POST", "/sales_credit_notes", json=payload)

    async def update_sales_credit_note(self, credit_note_id: str, payload: Dict[str, Any]):
        """Update an existing sales credit note"""
        return await self._request("PUT", f"/sales_credit_notes/{credit_note_id}", json=payload)

    async def delete_sales_credit_note(self, credit_note_id: str):
        """Delete a sales credit note"""
        return await self._request("DELETE", f"/sales_credit_notes/{credit_note_id}")

    # ============================================================================
    # CONTACTS METHODS
    # ============================================================================

    async def list_contacts(self, search: Optional[str]=None, items_per_page: int=50):
        """List all contacts"""
        params = {"items_per_page": items_per_page}
        if search:
            params["search"] = search
        return await self._request("GET", "/contacts", params=params)

    async def get_contact(self, contact_id: str):
        """Get a specific contact by ID"""
        return await self._request("GET", f"/contacts/{contact_id}")

    async def create_contact(self, payload: Dict[str, Any]):
        """Create a new contact"""
        return await self._request("POST", "/contacts", json=payload)

    async def update_contact(self, contact_id: str, payload: Dict[str, Any]):
        """Update an existing contact"""
        return await self._request("PUT", f"/contacts/{contact_id}", json=payload)

    async def delete_contact(self, contact_id: str):
        """Delete a contact"""
        return await self._request("DELETE", f"/contacts/{contact_id}")
