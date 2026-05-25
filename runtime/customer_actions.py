"""
Customer Actions

Actions for managing customers in the foreign trade system.
Uses real database-backed implementations via SQLModel/SQLite.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from infrastructure.database import (
    get_db_session,
    init_db,
    Lead,
    Customer,
    CustomerRepository,
    LeadRepository,
)


class CustomerActions:
    """Handler for customer-related actions using database persistence."""

    def __init__(self):
        """Initialize database on first use."""
        init_db()

    def create_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer in the database.
        
        Required params: company_name, contact_name, contact_email, country
        Optional params: contact_phone, address, business_type, source_channel, 
                        notes, phone, website, trade_terms
        """
        # Normalize Chinese field names to English
        _field_map = {
            "公司名称": "company_name", "国家": "country", "来源渠道": "source_channel",
            "联系人": "contact_name", "电话": "phone", "备注": "notes",
            "官网": "website", "业务类型": "business_type", "发信时间": "send_time_window",
            "联系状态": "contact_status", "下次跟进日期": "next_follow_up_date",
            "跟进记录": "follow_up_records",
        }
        for cn, en in _field_map.items():
            if cn in params and en not in params:
                params[en] = params[cn]

        required = ["company_name", "country"]
        for field in required:
            if field not in params:
                return {"error": f"Missing required field: {field}"}

        try:
            with get_db_session() as session:
                repo = CustomerRepository(session)
                
                # Generate unique customer_id
                customer_id = f"cust_{datetime.utcnow().strftime('%Y%m%d')}_{str(uuid.uuid4())[:6]}"
                
                customer = Customer(
                    customer_id=customer_id,
                    company_name=params["company_name"],
                    contact_status="new",
                    country=params["country"],
                    business_type=params.get("business_type"),
                    source_channel=params.get("source_channel"),
                    notes=params.get("notes"),
                    send_time_window=params.get("send_time_window"),
                    phone=params.get("phone"),
                    website=params.get("website"),
                )
                
                repo.create(customer)
                
                # Also create a Lead record for tracking
                lead = Lead(
                    lead_id=f"lead_{datetime.utcnow().strftime('%Y%m%d')}_{str(uuid.uuid4())[:6]}",
                    company_name=params["company_name"],
                    contact_name=params.get("contact_name", ""),
                    contact_email=params.get("contact_email", ""),
                    contact_phone=params.get("contact_phone"),
                    country=params["country"],
                    source=params.get("source_channel", "manual"),
                    status="converted",
                )
                lead_repo = LeadRepository(session)
                lead_repo.create(lead)
                
                return {
                    "customer_id": customer_id,
                    "company_name": customer.company_name,
                    "contact_status": customer.contact_status,
                    "country": customer.country,
                    "business_type": customer.business_type,
                    "source_channel": customer.source_channel,
                    "notes": customer.notes,
                    "phone": customer.phone,
                    "website": customer.website,
                    "created_at": customer.created_at.isoformat() if customer.created_at else datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {"error": str(e)}

    def get_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get customer details by customer_id.
        
        Required params: customer_id
        """
        if "customer_id" not in params:
            return {"error": "Missing required field: customer_id"}

        try:
            with get_db_session() as session:
                repo = CustomerRepository(session)
                customer = repo.get_by_customer_id(params["customer_id"])
                
                if not customer:
                    return {"error": f"Customer not found: {params['customer_id']}"}
                
                return {
                    "customer_id": customer.customer_id,
                    "company_name": customer.company_name,
                    "country": customer.country,
                    "business_type": customer.business_type,
                    "source_channel": customer.source_channel,
                    "contact_status": customer.contact_status,
                    "next_follow_up_date": customer.next_follow_up_date,
                    "follow_up_records": customer.follow_up_records,
                    "notes": customer.notes,
                    "phone": customer.phone,
                    "website": customer.website,
                    "created_at": customer.created_at.isoformat() if customer.created_at else None
                }
        except Exception as e:
            return {"error": str(e)}

    def update_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update customer information.
        
        Required params: customer_id
        Optional params: company_name, contact_status, next_follow_up_date, 
                        follow_up_records, notes, phone, website, business_type
        """
        if "customer_id" not in params:
            return {"error": "Missing required field: customer_id"}

        try:
            with get_db_session() as session:
                repo = CustomerRepository(session)
                customer = repo.get_by_customer_id(params["customer_id"])
                
                if not customer:
                    return {"error": f"Customer not found: {params['customer_id']}"}
                
                # Update allowed fields
                updatable_fields = [
                    "company_name", "contact_status", "next_follow_up_date",
                    "follow_up_records", "notes", "phone", "website", 
                    "business_type", "source_channel", "send_time_window"
                ]
                updated_fields = {}
                for field in updatable_fields:
                    if field in params:
                        setattr(customer, field, params[field])
                        updated_fields[field] = params[field]
                
                repo.update(customer)
                
                return {
                    "customer_id": customer.customer_id,
                    "updated_fields": updated_fields,
                    "updated_at": customer.updated_at.isoformat() if customer.updated_at else datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {"error": str(e)}

    def list_customers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all customers with optional filtering and pagination.
        
        Optional params: page, per_page, country, contact_status
        """
        page = params.get("page", 1)
        per_page = params.get("per_page", 20)
        country = params.get("country")
        contact_status = params.get("contact_status")
        offset = (page - 1) * per_page

        try:
            with get_db_session() as session:
                repo = CustomerRepository(session)
                
                if country:
                    customers = repo.get_by_country(country, offset=offset, limit=per_page)
                    total = len(repo.get_by_country(country, offset=0, limit=10000))
                elif contact_status:
                    customers = repo.get_by_contact_status(contact_status, offset=offset, limit=per_page)
                    total = len(repo.get_by_contact_status(contact_status, offset=0, limit=10000))
                else:
                    customers = repo.get_all(offset=offset, limit=per_page, active_only=True)
                    total = repo.count(active_only=True)
                
                customer_list = [
                    {
                        "customer_id": c.customer_id,
                        "company_name": c.company_name,
                        "country": c.country,
                        "contact_status": c.contact_status,
                        "business_type": c.business_type,
                        "source_channel": c.source_channel,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                    }
                    for c in customers
                ]
                
                return {
                    "customers": customer_list,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": total
                    }
                }
        except Exception as e:
            return {"error": str(e)}

    def delete_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Soft delete a customer by setting contact_status to 'deleted'.
        
        Required params: customer_id
        """
        if "customer_id" not in params:
            return {"error": "Missing required field: customer_id"}

        try:
            with get_db_session() as session:
                repo = CustomerRepository(session)
                # Get the internal id first
                customer = repo.get_by_customer_id(params["customer_id"])
                
                if not customer:
                    return {"error": f"Customer not found: {params['customer_id']}"}
                
                success = repo.delete(customer.id)
                
                return {
                    "success": success,
                    "customer_id": params["customer_id"],
                    "deleted": success
                }
        except Exception as e:
            return {"error": str(e)}

    def get_customer_orders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get leads/orders associated with a customer.
        In this system, leads represent potential orders/quoting requests.
        
        Required params: customer_id
        """
        if "customer_id" not in params:
            return {"error": "Missing required field: customer_id"}

        try:
            with get_db_session() as session:
                lead_repo = LeadRepository(session)
                customer_repo = CustomerRepository(session)
                
                customer = customer_repo.get_by_customer_id(params["customer_id"])
                if not customer:
                    return {"error": f"Customer not found: {params['customer_id']}"}
                
                # Get leads by company name (since lead doesn't have customer_id directly)
                # In a real system, there would be a proper foreign key relationship
                all_leads = lead_repo.get_all(offset=0, limit=100)
                customer_leads = [
                    l for l in all_leads 
                    if l.company_name == customer.company_name or l.status == "converted"
                ]
                
                return {
                    "customer_id": params["customer_id"],
                    "orders": [
                        {
                            "lead_id": lead.lead_id,
                            "company_name": lead.company_name,
                            "contact_name": lead.contact_name,
                            "contact_email": lead.contact_email,
                            "status": lead.status,
                            "product_interest": lead.product_interest,
                            "target_quantity": lead.target_quantity,
                            "target_price": lead.target_price,
                            "created_at": lead.created_at.isoformat() if lead.created_at else None,
                        }
                        for lead in customer_leads
                    ]
                }
        except Exception as e:
            return {"error": str(e)}

    def add_follow_up_record(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a follow-up record to a customer's history.
        
        Required params: customer_id, follow_up_record
        Optional params: next_follow_up_date
        """
        if "customer_id" not in params:
            return {"error": "Missing required field: customer_id"}
        if "follow_up_record" not in params:
            return {"error": "Missing required field: follow_up_record"}

        try:
            with get_db_session() as session:
                repo = CustomerRepository(session)
                customer = repo.get_by_customer_id(params["customer_id"])
                
                if not customer:
                    return {"error": f"Customer not found: {params['customer_id']}"}
                
                # Append to existing follow-up records
                existing_records = customer.follow_up_records or ""
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
                new_record = f"[{timestamp}] {params['follow_up_record']}"
                
                if existing_records:
                    customer.follow_up_records = f"{existing_records}\n{new_record}"
                else:
                    customer.follow_up_records = new_record
                
                # Update next follow-up date if provided
                if "next_follow_up_date" in params:
                    customer.next_follow_up_date = params["next_follow_up_date"]
                
                # Update contact status to indicate follow-up happened
                if customer.contact_status == "new":
                    customer.contact_status = "contacted"
                
                repo.update(customer)
                
                return {
                    "customer_id": customer.customer_id,
                    "follow_up_record": new_record,
                    "follow_up_records": customer.follow_up_records,
                    "next_follow_up_date": customer.next_follow_up_date,
                    "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
                }
        except Exception as e:
            return {"error": str(e)}

    def get_customer_by_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get or create a customer from a lead.
        
        Required params: lead_id
        """
        if "lead_id" not in params:
            return {"error": "Missing required field: lead_id"}

        try:
            with get_db_session() as session:
                lead_repo = LeadRepository(session)
                customer_repo = CustomerRepository(session)
                
                lead = lead_repo.get_by_lead_id(params["lead_id"])
                if not lead:
                    return {"error": f"Lead not found: {params['lead_id']}"}
                
                # Check if customer already exists for this lead
                existing_customer = customer_repo.get_by_customer_id(f"cust_from_lead_{params['lead_id']}")
                if existing_customer:
                    return {
                        "success": True,
                        "customer_id": existing_customer.customer_id,
                        "data": {
                            "company_name": existing_customer.company_name,
                            "country": existing_customer.country,
                            "contact_status": existing_customer.contact_status,
                        },
                        "is_new": False
                    }
                
                # Create new customer from lead
                customer_id = f"cust_from_lead_{params['lead_id']}"
                customer = Customer(
                    customer_id=customer_id,
                    company_name=lead.company_name,
                    contact_status="new",
                    country=lead.country,
                    source_channel=lead.source,
                    phone=lead.contact_phone,
                    website=lead.website,
                )
                customer_repo.create(customer)
                
                # Update lead status
                lead.status = "converted"
                lead_repo.update(lead)
                
                return {
                    "customer_id": customer_id,
                    "company_name": customer.company_name,
                    "country": customer.country,
                    "contact_status": customer.contact_status,
                    "is_new": True
                }
        except Exception as e:
            return {"error": str(e)}
