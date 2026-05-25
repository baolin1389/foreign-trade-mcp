"""MCP tools for foreign trade business automation.

This module provides FastMCP tools that wrap engine.execute() calls
to the Foreign Trade MCP engine (lead, customer, email domains).
"""

import sys
import os
from typing import Any, Dict, List, Optional

# Add the project root to the path for imports
project_root = os.path.dirname(os.path.dirname(__file__))
runtime_path = os.path.join(project_root, 'runtime')
if runtime_path not in sys.path:
    sys.path.insert(0, runtime_path)

from runtime.engine import Engine


# Global engine instance
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """Get or create the global engine instance."""
    global _engine
    if _engine is None:
        _engine = Engine()
    return _engine


# =============================================================================
# Lead Actions
# =============================================================================

def create_lead(
    company_name: str,
    contact_name: str,
    email: str,
    phone: Optional[str] = None,
    source: Optional[str] = None
) -> dict:
    """Create a new lead.
    
    Args:
        company_name: Name of the company.
        contact_name: Name of the contact person.
        email: Contact email address.
        phone: Optional phone number.
        source: Optional lead source (default: 'direct').
        
    Returns:
        Created lead information.
    """
    engine = get_engine()
    params: Dict[str, Any] = {
        "company_name": company_name,
        "contact_name": contact_name,
        "email": email
    }
    if phone:
        params["phone"] = phone
    if source:
        params["source"] = source
    
    return engine.execute("lead", "create_lead", params)


def get_lead(lead_id: str) -> dict:
    """Get lead details by ID.
    
    Args:
        lead_id: The unique lead identifier.
        
    Returns:
        Lead details.
    """
    engine = get_engine()
    return engine.execute("lead", "get_lead", {"lead_id": lead_id})


def update_lead(lead_id: str, **kwargs: Any) -> dict:
    """Update an existing lead.
    
    Args:
        lead_id: The unique lead identifier.
        **kwargs: Fields to update (company_name, contact_name, email, phone, status, etc.).
        
    Returns:
        Update confirmation with changed fields.
    """
    engine = get_engine()
    params: Dict[str, Any] = {"lead_id": lead_id, **kwargs}
    return engine.execute("lead", "update_lead", params)


def list_leads(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None
) -> dict:
    """List all leads with optional filtering.
    
    Args:
        page: Page number (default: 1).
        per_page: Items per page (default: 20).
        status: Optional status filter ('new', 'contacted', 'qualified').
        
    Returns:
        Paginated list of leads.
    """
    engine = get_engine()
    params: Dict[str, Any] = {"page": page, "per_page": per_page}
    if status:
        params["status"] = status
    return engine.execute("lead", "list_leads", params)


def delete_lead(lead_id: str) -> dict:
    """Delete a lead.
    
    Args:
        lead_id: The unique lead identifier.
        
    Returns:
        Deletion confirmation.
    """
    engine = get_engine()
    return engine.execute("lead", "delete_lead", {"lead_id": lead_id})


def convert_lead(lead_id: str) -> dict:
    """Convert a lead to a customer.
    
    Args:
        lead_id: The unique lead identifier.
        
    Returns:
        Conversion confirmation with new customer_id.
    """
    engine = get_engine()
    return engine.execute("lead", "convert_lead", {"lead_id": lead_id})


# =============================================================================
# Customer Actions
# =============================================================================

def create_customer(
    company_name: str,
    contact_name: str,
    email: str,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    country: Optional[str] = None,
    trade_terms: Optional[str] = None
) -> dict:
    """Create a new customer.
    
    Args:
        company_name: Name of the company.
        contact_name: Name of the contact person.
        email: Contact email address.
        phone: Optional phone number.
        address: Optional address.
        country: Optional country.
        trade_terms: Optional trade terms (default: 'FOB').
        
    Returns:
        Created customer information.
    """
    engine = get_engine()
    params: Dict[str, Any] = {
        "company_name": company_name,
        "contact_name": contact_name,
        "email": email
    }
    if phone:
        params["phone"] = phone
    if address:
        params["address"] = address
    if country:
        params["country"] = country
    if trade_terms:
        params["trade_terms"] = trade_terms
    
    return engine.execute("customer", "create_customer", params)


def get_customer(customer_id: str) -> dict:
    """Get customer details by ID.
    
    Args:
        customer_id: The unique customer identifier.
        
    Returns:
        Customer details.
    """
    engine = get_engine()
    return engine.execute("customer", "get_customer", {"customer_id": customer_id})


def update_customer(customer_id: str, **kwargs: Any) -> dict:
    """Update customer information.
    
    Args:
        customer_id: The unique customer identifier.
        **kwargs: Fields to update (company_name, contact_name, email, phone, country, trade_terms, etc.).
        
    Returns:
        Update confirmation with changed fields.
    """
    engine = get_engine()
    params: Dict[str, Any] = {"customer_id": customer_id, **kwargs}
    return engine.execute("customer", "update_customer", params)


def list_customers(
    page: int = 1,
    per_page: int = 20,
    country: Optional[str] = None
) -> dict:
    """List all customers.
    
    Args:
        page: Page number (default: 1).
        per_page: Items per page (default: 20).
        country: Optional country filter.
        
    Returns:
        Paginated list of customers.
    """
    engine = get_engine()
    params: Dict[str, Any] = {"page": page, "per_page": per_page}
    if country:
        params["country"] = country
    return engine.execute("customer", "list_customers", params)


def delete_customer(customer_id: str) -> dict:
    """Delete a customer.
    
    Args:
        customer_id: The unique customer identifier.
        
    Returns:
        Deletion confirmation.
    """
    engine = get_engine()
    return engine.execute("customer", "delete_customer", {"customer_id": customer_id})


def get_customer_orders(customer_id: str) -> dict:
    """Get orders for a specific customer.
    
    Args:
        customer_id: The unique customer identifier.
        
    Returns:
        List of customer orders.
    """
    engine = get_engine()
    return engine.execute("customer", "get_customer_orders", {"customer_id": customer_id})


# =============================================================================
# Email Actions
# =============================================================================

def send_email(
    to: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None
) -> dict:
    """Send an email.
    
    Args:
        to: Recipient email address.
        subject: Email subject.
        body: Email body content.
        from_email: Optional sender email (defaults to system default).
        
    Returns:
        Send confirmation with email_id.
    """
    engine = get_engine()
    params: Dict[str, Any] = {
        "to": to,
        "subject": subject,
        "body": body
    }
    if from_email:
        params["from"] = from_email
    return engine.execute("email", "send_email", params)


def get_email(email_id: str) -> dict:
    """Get email details by ID.
    
    Args:
        email_id: The unique email identifier.
        
    Returns:
        Email details.
    """
    engine = get_engine()
    return engine.execute("email", "get_email", {"email_id": email_id})


def list_emails(
    page: int = 1,
    per_page: int = 20,
    folder: str = "inbox"
) -> dict:
    """List emails with optional filtering.
    
    Args:
        page: Page number (default: 1).
        per_page: Items per page (default: 20).
        folder: Folder to list ('inbox', 'sent', 'drafts', etc.).
        
    Returns:
        Paginated list of emails.
    """
    engine = get_engine()
    params: Dict[str, Any] = {"page": page, "per_page": per_page, "folder": folder}
    return engine.execute("email", "list_emails", params)


def delete_email(email_id: str) -> dict:
    """Delete an email.
    
    Args:
        email_id: The unique email identifier.
        
    Returns:
        Deletion confirmation.
    """
    engine = get_engine()
    return engine.execute("email", "delete_email", {"email_id": email_id})


def send_bulk_emails(
    recipients: List[str],
    subject: str,
    body: str
) -> dict:
    """Send bulk emails to multiple recipients.
    
    Args:
        recipients: List of recipient email addresses.
        subject: Email subject.
        body: Email body content.
        
    Returns:
        Bulk send results with sent/failed counts.
    """
    engine = get_engine()
    params: Dict[str, Any] = {
        "recipients": recipients,
        "subject": subject,
        "body": body
    }
    return engine.execute("email", "send_bulk_emails", params)


def mark_email_as_read(email_id: str) -> dict:
    """Mark an email as read.
    
    Args:
        email_id: The unique email identifier.
        
    Returns:
        Update confirmation.
    """
    engine = get_engine()
    return engine.execute("email", "mark_as_read", {"email_id": email_id})
