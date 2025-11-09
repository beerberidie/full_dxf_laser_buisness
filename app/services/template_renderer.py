"""
Template Renderer Service for Laser OS.

This service handles rendering message templates with dynamic placeholders.
Supports placeholders like {{client_name}}, {{project_code}}, etc.

Phase 2 Implementation - Message Templates.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import current_app

from app.models import Client, Project, Quote, Invoice


class TemplateRenderer:
    """
    Renders message templates with dynamic data.
    
    Supports placeholders:
        {{client_name}} - Client name
        {{client_code}} - Client code
        {{client_email}} - Client email
        {{client_phone}} - Client phone
        {{client_contact}} - Client contact person
        {{project_code}} - Project code
        {{project_name}} - Project name
        {{project_status}} - Project status
        {{collection_date}} - Calculated collection date
        {{quote_total}} - Quote total amount
        {{invoice_total}} - Invoice total amount
        {{company_name}} - Company name from config
        {{current_date}} - Current date
        {{current_time}} - Current time
        {{current_datetime}} - Current date and time
    """
    
    def __init__(self):
        """Initialize the template renderer."""
        self.placeholders = {}
    
    def render(
        self,
        template_text: str,
        client_id: Optional[int] = None,
        project_id: Optional[int] = None,
        quote_id: Optional[int] = None,
        invoice_id: Optional[int] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render a template with dynamic data.
        
        Args:
            template_text: Template text with placeholders
            client_id: Optional client ID for client data
            project_id: Optional project ID for project data
            quote_id: Optional quote ID for quote data
            invoice_id: Optional invoice ID for invoice data
            custom_data: Optional custom placeholder data
        
        Returns:
            str: Rendered template with placeholders replaced
        
        Example:
            >>> renderer = TemplateRenderer()
            >>> result = renderer.render(
            ...     "Dear {{client_name}}, your order {{project_code}} is ready.",
            ...     client_id=1,
            ...     project_id=5
            ... )
            >>> print(result)
            "Dear ABC Company, your order PRJ-0005 is ready."
        """
        # Build placeholder data
        self.placeholders = {}
        
        # Add system placeholders
        self._add_system_placeholders()
        
        # Add client data
        if client_id:
            self._add_client_placeholders(client_id)
        
        # Add project data
        if project_id:
            self._add_project_placeholders(project_id)
        
        # Add quote data
        if quote_id:
            self._add_quote_placeholders(quote_id)
        
        # Add invoice data
        if invoice_id:
            self._add_invoice_placeholders(invoice_id)
        
        # Add custom data (overrides any existing placeholders)
        if custom_data:
            self.placeholders.update(custom_data)
        
        # Render template
        rendered = template_text
        for key, value in self.placeholders.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def _add_system_placeholders(self):
        """Add system-level placeholders."""
        now = datetime.now()
        
        self.placeholders.update({
            'company_name': current_app.config.get('COMPANY_NAME', 'Laser OS'),
            'current_date': now.strftime('%Y-%m-%d'),
            'current_time': now.strftime('%H:%M:%S'),
            'current_datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
            'current_year': str(now.year),
        })
    
    def _add_client_placeholders(self, client_id: int):
        """Add client-related placeholders."""
        client = Client.query.get(client_id)
        
        if client:
            self.placeholders.update({
                'client_name': client.name or '',
                'client_code': client.client_code or '',
                'client_email': client.email or '',
                'client_phone': client.phone or '',
                'client_contact': client.contact_person or '',
                'client_address': client.address or '',
            })
    
    def _add_project_placeholders(self, project_id: int):
        """Add project-related placeholders."""
        project = Project.query.get(project_id)
        
        if project:
            # Calculate collection date (3 days after completion or current date + SLA)
            collection_date = None
            if project.status == 'Complete' and project.updated_at:
                collection_date = project.updated_at + timedelta(days=3)
            elif project.created_at:
                sla_days = current_app.config.get('DEFAULT_SLA_DAYS', 3)
                collection_date = project.created_at + timedelta(days=sla_days)
            
            self.placeholders.update({
                'project_code': project.project_code or '',
                'project_name': project.project_name or '',
                'project_status': project.status or '',
                'project_description': project.description or '',
                'project_quantity': str(project.quantity) if project.quantity else '',
                'project_material': project.material or '',
                'project_thickness': str(project.thickness) if project.thickness else '',
                'collection_date': collection_date.strftime('%Y-%m-%d') if collection_date else '',
            })
            
            # Add client data from project if not already added
            if project.client_id and 'client_name' not in self.placeholders:
                self._add_client_placeholders(project.client_id)
    
    def _add_quote_placeholders(self, quote_id: int):
        """Add quote-related placeholders."""
        quote = Quote.query.get(quote_id)
        
        if quote:
            self.placeholders.update({
                'quote_code': quote.quote_code or '',
                'quote_total': f'R {quote.total_amount:,.2f}' if quote.total_amount else 'R 0.00',
                'quote_status': quote.status or '',
                'quote_valid_until': quote.valid_until.strftime('%Y-%m-%d') if quote.valid_until else '',
            })
            
            # Add client data from quote if not already added
            if quote.client_id and 'client_name' not in self.placeholders:
                self._add_client_placeholders(quote.client_id)
    
    def _add_invoice_placeholders(self, invoice_id: int):
        """Add invoice-related placeholders."""
        invoice = Invoice.query.get(invoice_id)
        
        if invoice:
            self.placeholders.update({
                'invoice_code': invoice.invoice_code or '',
                'invoice_total': f'R {invoice.total_amount:,.2f}' if invoice.total_amount else 'R 0.00',
                'invoice_status': invoice.status or '',
                'invoice_due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
            })
            
            # Add client data from invoice if not already added
            if invoice.client_id and 'client_name' not in self.placeholders:
                self._add_client_placeholders(invoice.client_id)
    
    def get_available_placeholders(self) -> Dict[str, str]:
        """
        Get a dictionary of all available placeholders and their descriptions.
        
        Returns:
            dict: Placeholder names and descriptions
        """
        return {
            # System placeholders
            'company_name': 'Your company name',
            'current_date': 'Current date (YYYY-MM-DD)',
            'current_time': 'Current time (HH:MM:SS)',
            'current_datetime': 'Current date and time',
            'current_year': 'Current year',
            
            # Client placeholders
            'client_name': 'Client company name',
            'client_code': 'Client code (CL-xxxx)',
            'client_email': 'Client email address',
            'client_phone': 'Client phone number',
            'client_contact': 'Client contact person name',
            'client_address': 'Client physical address',
            
            # Project placeholders
            'project_code': 'Project code (PRJ-xxxx)',
            'project_name': 'Project name',
            'project_status': 'Project status',
            'project_description': 'Project description',
            'project_quantity': 'Project quantity',
            'project_material': 'Project material',
            'project_thickness': 'Material thickness',
            'collection_date': 'Calculated collection date',
            
            # Quote placeholders
            'quote_code': 'Quote code (QT-xxxx)',
            'quote_total': 'Quote total amount (formatted)',
            'quote_status': 'Quote status',
            'quote_valid_until': 'Quote validity date',
            
            # Invoice placeholders
            'invoice_code': 'Invoice code (INV-xxxx)',
            'invoice_total': 'Invoice total amount (formatted)',
            'invoice_status': 'Invoice status',
            'invoice_due_date': 'Invoice due date',
        }


def render_template(
    template_text: str,
    client_id: Optional[int] = None,
    project_id: Optional[int] = None,
    quote_id: Optional[int] = None,
    invoice_id: Optional[int] = None,
    custom_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to render a template.
    
    Args:
        template_text: Template text with placeholders
        client_id: Optional client ID
        project_id: Optional project ID
        quote_id: Optional quote ID
        invoice_id: Optional invoice ID
        custom_data: Optional custom data
    
    Returns:
        str: Rendered template
    
    Example:
        >>> result = render_template(
        ...     "Dear {{client_name}}, your order {{project_code}} is ready.",
        ...     client_id=1,
        ...     project_id=5
        ... )
    """
    renderer = TemplateRenderer()
    return renderer.render(
        template_text,
        client_id=client_id,
        project_id=project_id,
        quote_id=quote_id,
        invoice_id=invoice_id,
        custom_data=custom_data
    )


def get_available_placeholders() -> Dict[str, str]:
    """
    Get all available placeholders and their descriptions.
    
    Returns:
        dict: Placeholder names and descriptions
    """
    renderer = TemplateRenderer()
    return renderer.get_available_placeholders()

