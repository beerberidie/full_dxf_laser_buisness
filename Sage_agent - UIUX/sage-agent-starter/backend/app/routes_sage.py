from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from typing import Optional
from .sage_v31 import SageV31Client

router = APIRouter(prefix="/api/sage", tags=["sage"])

def _tenant_id() -> str:
    return "demo-tenant"

# ============================================================================
# QUOTES ENDPOINTS
# ============================================================================

@router.get("/sales_quotes")
async def list_sales_quotes(updated_since: Optional[str] = Query(default=None)):
    """List all sales quotes"""
    client = SageV31Client(_tenant_id())
    return await client.list_sales_quotes(updated_since=updated_since, items_per_page=50)

@router.get("/sales_quotes/{quote_id}")
async def get_sales_quote(quote_id: str):
    """Get a specific sales quote by ID"""
    client = SageV31Client(_tenant_id())
    return await client.get_sales_quote(quote_id)

@router.post("/sales_quotes")
async def create_sales_quote(payload: dict):
    """Create a new sales quote"""
    client = SageV31Client(_tenant_id())
    return await client.create_sales_quote(payload)

@router.put("/sales_quotes/{quote_id}")
async def update_sales_quote(quote_id: str, payload: dict):
    """Update an existing sales quote"""
    client = SageV31Client(_tenant_id())
    return await client.update_sales_quote(quote_id, payload)

@router.delete("/sales_quotes/{quote_id}")
async def delete_sales_quote(quote_id: str):
    """Delete a sales quote"""
    client = SageV31Client(_tenant_id())
    return await client.delete_sales_quote(quote_id)

# ============================================================================
# ESTIMATES ENDPOINTS
# ============================================================================

@router.get("/sales_estimates")
async def list_sales_estimates(updated_since: Optional[str] = Query(default=None)):
    """List all sales estimates"""
    client = SageV31Client(_tenant_id())
    return await client.list_sales_estimates(updated_since=updated_since, items_per_page=50)

@router.get("/sales_estimates/{estimate_id}")
async def get_sales_estimate(estimate_id: str):
    """Get a specific sales estimate by ID"""
    client = SageV31Client(_tenant_id())
    return await client.get_sales_estimate(estimate_id)

@router.post("/sales_estimates")
async def create_sales_estimate(payload: dict):
    """Create a new sales estimate"""
    client = SageV31Client(_tenant_id())
    return await client.create_sales_estimate(payload)

@router.put("/sales_estimates/{estimate_id}")
async def update_sales_estimate(estimate_id: str, payload: dict):
    """Update an existing sales estimate"""
    client = SageV31Client(_tenant_id())
    return await client.update_sales_estimate(estimate_id, payload)

@router.delete("/sales_estimates/{estimate_id}")
async def delete_sales_estimate(estimate_id: str):
    """Delete a sales estimate"""
    client = SageV31Client(_tenant_id())
    return await client.delete_sales_estimate(estimate_id)

# ============================================================================
# INVOICES ENDPOINTS
# ============================================================================

@router.get("/sales_invoices")
async def list_sales_invoices(updated_since: Optional[str] = Query(default=None)):
    """List all sales invoices"""
    client = SageV31Client(_tenant_id())
    return await client.list_sales_invoices(updated_since=updated_since, items_per_page=50)

@router.get("/sales_invoices/{invoice_id}")
async def get_sales_invoice(invoice_id: str):
    """Get a specific sales invoice by ID"""
    client = SageV31Client(_tenant_id())
    return await client.get_sales_invoice(invoice_id)

@router.post("/sales_invoices")
async def create_sales_invoice(payload: dict):
    """Create a new sales invoice"""
    client = SageV31Client(_tenant_id())
    return await client.create_sales_invoice(payload)

@router.put("/sales_invoices/{invoice_id}")
async def update_sales_invoice(invoice_id: str, payload: dict):
    """Update an existing sales invoice"""
    client = SageV31Client(_tenant_id())
    return await client.update_sales_invoice(invoice_id, payload)

@router.delete("/sales_invoices/{invoice_id}")
async def delete_sales_invoice(invoice_id: str):
    """Delete a sales invoice"""
    client = SageV31Client(_tenant_id())
    return await client.delete_sales_invoice(invoice_id)

@router.post("/sales_invoices/{invoice_id}/release")
async def release_sales_invoice(invoice_id: str):
    """Release (finalize) a sales invoice"""
    client = SageV31Client(_tenant_id())
    return await client.release_sales_invoice(invoice_id)

# ============================================================================
# CREDIT NOTES ENDPOINTS
# ============================================================================

@router.get("/sales_credit_notes")
async def list_sales_credit_notes(updated_since: Optional[str] = Query(default=None)):
    """List all sales credit notes"""
    client = SageV31Client(_tenant_id())
    return await client.list_sales_credit_notes(updated_since=updated_since, items_per_page=50)

@router.get("/sales_credit_notes/{credit_note_id}")
async def get_sales_credit_note(credit_note_id: str):
    """Get a specific sales credit note by ID"""
    client = SageV31Client(_tenant_id())
    return await client.get_sales_credit_note(credit_note_id)

@router.post("/sales_credit_notes")
async def create_sales_credit_note(payload: dict):
    """Create a new sales credit note"""
    client = SageV31Client(_tenant_id())
    return await client.create_sales_credit_note(payload)

@router.put("/sales_credit_notes/{credit_note_id}")
async def update_sales_credit_note(credit_note_id: str, payload: dict):
    """Update an existing sales credit note"""
    client = SageV31Client(_tenant_id())
    return await client.update_sales_credit_note(credit_note_id, payload)

@router.delete("/sales_credit_notes/{credit_note_id}")
async def delete_sales_credit_note(credit_note_id: str):
    """Delete a sales credit note"""
    client = SageV31Client(_tenant_id())
    return await client.delete_sales_credit_note(credit_note_id)

# ============================================================================
# CONTACTS ENDPOINTS
# ============================================================================

@router.get("/contacts")
async def list_contacts(search: Optional[str] = None):
    """List all contacts"""
    client = SageV31Client(_tenant_id())
    return await client.list_contacts(search=search)

@router.get("/contacts/{contact_id}")
async def get_contact(contact_id: str):
    """Get a specific contact by ID"""
    client = SageV31Client(_tenant_id())
    return await client.get_contact(contact_id)

@router.post("/contacts")
async def create_contact(payload: dict):
    """Create a new contact"""
    client = SageV31Client(_tenant_id())
    return await client.create_contact(payload)

@router.put("/contacts/{contact_id}")
async def update_contact(contact_id: str, payload: dict):
    """Update an existing contact"""
    client = SageV31Client(_tenant_id())
    return await client.update_contact(contact_id, payload)

@router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str):
    """Delete a contact"""
    client = SageV31Client(_tenant_id())
    return await client.delete_contact(contact_id)
