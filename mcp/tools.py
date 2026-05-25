"""MCP tools for foreign trade business automation.

This module provides FastMCP tools that wrap engine.execute() calls.
Each tool is a thin wrapper — no business logic here.

MCP Tool Signature Convention:
    tool_xxx(params) → engine.execute("xxx", params)
    Tool name matches action name exactly.
"""

import sys
import os
from typing import Any, Dict, List, Optional

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from runtime.engine import Engine


# Global engine instance (lazy singleton)
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """Get or create the global engine instance."""
    global _engine
    if _engine is None:
        _engine = Engine()
    return _engine


# =============================================================================
# Lead Tools
# =============================================================================

def create_lead(
    company_name: str,
    contact_name: str,
    contact_email: str,
    country: str,
    contact_phone: Optional[str] = None,
    source: Optional[str] = None,
    product_interest: Optional[str] = None,
    website: Optional[str] = None,
    status: str = "new",
) -> dict:
    """
    Create a new lead record.

    Required: company_name, contact_name, contact_email, country
    Optional: contact_phone, source, product_interest, website, status
    """
    engine = get_engine()
    params = {
        "company_name": company_name,
        "contact_name": contact_name,
        "contact_email": contact_email,
        "country": country,
        "status": status,
    }
    if contact_phone:
        params["contact_phone"] = contact_phone
    if source:
        params["source"] = source
    if product_interest:
        params["product_interest"] = product_interest
    if website:
        params["website"] = website

    return engine.execute("lead.create_lead", params)


def get_lead(lead_id: str) -> dict:
    """Get a lead by lead_id."""
    engine = get_engine()
    return engine.execute("lead.get_lead", {"lead_id": lead_id})


def update_lead(lead_id: str, **kwargs: Any) -> dict:
    """Update a lead. Available fields: company_name, contact_name, contact_email, contact_phone, country, source, status, product_interest."""
    engine = get_engine()
    params = {"lead_id": lead_id, **kwargs}
    return engine.execute("lead.update_lead", params)


def list_leads(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    country: Optional[str] = None,
) -> dict:
    """List leads with pagination. Optional filters: status, country."""
    engine = get_engine()
    params = {"page": page, "page_size": page_size}
    if status:
        params["status"] = status
    if country:
        params["country"] = country
    return engine.execute("lead.list_leads", params)


def delete_lead(lead_id: str) -> dict:
    """Delete a lead by lead_id."""
    engine = get_engine()
    return engine.execute("lead.delete_lead", {"lead_id": lead_id})


def qualify_lead(lead_id: str, score: int, notes: Optional[str] = None) -> dict:
    """Qualify a lead with a score. Score must be >= 60."""
    engine = get_engine()
    params = {"lead_id": lead_id, "qualification_score": score}
    if notes:
        params["qualification_notes"] = notes
    return engine.execute("lead.qualify_lead", params)


def reject_lead(lead_id: str, reason: Optional[str] = None) -> dict:
    """Reject a lead."""
    engine = get_engine()
    params = {"lead_id": lead_id}
    if reason:
        params["qualification_notes"] = reason
    return engine.execute("lead.reject_lead", params)


def convert_lead(lead_id: str) -> dict:
    """Convert a qualified lead to a customer. Lead must be in 'qualified' status."""
    engine = get_engine()
    return engine.execute("lead.convert_lead", {"lead_id": lead_id})


# =============================================================================
# Customer Tools
# =============================================================================

def create_customer(
    company_name: str,
    country: str,
    contact_name: Optional[str] = None,
    contact_email: Optional[str] = None,
    contact_phone: Optional[str] = None,
    business_type: Optional[str] = None,
    source_channel: Optional[str] = None,
    notes: Optional[str] = None,
    contact_status: str = "new",
) -> dict:
    """
    Create a new customer record.

    Required: company_name, country
    Optional: contact_name, contact_email, contact_phone, business_type, source_channel, notes, contact_status
    """
    engine = get_engine()
    params = {
        "company_name": company_name,
        "country": country,
        "contact_status": contact_status,
    }
    if contact_name:
        params["contact_name"] = contact_name
    if contact_email:
        params["contact_email"] = contact_email
    if contact_phone:
        params["contact_phone"] = contact_phone
    if business_type:
        params["business_type"] = business_type
    if source_channel:
        params["source_channel"] = source_channel
    if notes:
        params["notes"] = notes

    return engine.execute("customer.create_customer", params)


def get_customer(customer_id: str) -> dict:
    """Get a customer by customer_id."""
    engine = get_engine()
    return engine.execute("customer.get_customer", {"customer_id": customer_id})


def update_customer(customer_id: str, **kwargs: Any) -> dict:
    """Update a customer. Available fields: contact_status, contact_name, contact_email, contact_phone, notes, next_follow_up_date."""
    engine = get_engine()
    params = {"customer_id": customer_id, **kwargs}
    return engine.execute("customer.update_customer", params)


def list_customers(
    page: int = 1,
    page_size: int = 20,
    contact_status: Optional[str] = None,
    country: Optional[str] = None,
) -> dict:
    """List customers with pagination. Optional filters: contact_status, country."""
    engine = get_engine()
    params = {"page": page, "page_size": page_size}
    if contact_status:
        params["contact_status"] = contact_status
    if country:
        params["country"] = country
    return engine.execute("customer.list_customers", params)


def delete_customer(customer_id: str) -> dict:
    """Soft-delete a customer (sets contact_status to 'deleted')."""
    engine = get_engine()
    return engine.execute("customer.delete_customer", {"customer_id": customer_id})


# =============================================================================
# Email Tools
# =============================================================================

def create_email_record(
    customer_id: str,
    to_email: str,
    from_email: str,
    subject: str,
    body: Optional[str] = None,
    status: str = "draft",
) -> dict:
    """
    Create a new email record (does NOT actually send email — use send_email for that).

    Required: customer_id, to_email, from_email, subject
    Optional: body, status
    """
    engine = get_engine()
    params = {
        "customer_id": customer_id,
        "to_email": to_email,
        "from_email": from_email,
        "subject": subject,
        "status": status,
    }
    if body:
        params["body"] = body
    return engine.execute("email.create_email_record", params)


def send_email(
    customer_id: str,
    to_email: str,
    from_email: str,
    subject: str,
    body: Optional[str] = None,
    first_send_status: str = "sent",
) -> dict:
    """
    Send an email and record it. Creates/updates EmailRecord with send timestamp.

    Required: customer_id, to_email, from_email, subject
    Optional: body, first_send_status
    """
    engine = get_engine()
    params = {
        "customer_id": customer_id,
        "to_email": to_email,
        "from_email": from_email,
        "subject": subject,
        "first_send_time": "now",
        "first_send_status": first_send_status,
    }
    if body:
        params["body"] = body
    return engine.execute("email.send_email", params)


def get_email_record(email_id: str) -> dict:
    """Get an email record by email_id."""
    engine = get_engine()
    return engine.execute("email.get_email_record", {"email_id": email_id})


def list_email_records(
    page: int = 1,
    page_size: int = 20,
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """List email records with pagination. Optional filters: customer_id, status."""
    engine = get_engine()
    params = {"page": page, "page_size": page_size}
    if customer_id:
        params["customer_id"] = customer_id
    if status:
        params["status"] = status
    return engine.execute("email.list_email_records", params)


def delete_email_record(email_id: str) -> dict:
    """Delete an email record by email_id."""
    engine = get_engine()
    return engine.execute("email.delete_email_record", {"email_id": email_id})