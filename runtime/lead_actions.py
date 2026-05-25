"""
Lead Actions

Actions for managing leads in the foreign trade system.
Database-backed implementation using SQLite and SQLModel.
"""

from typing import Any, Dict, Optional
from datetime import datetime

from infrastructure.database import (
    Lead,
    LeadRepository,
    Customer,
    CustomerRepository,
    get_db_session,
)


class LeadActions:
    """Handler for lead-related actions with real database operations."""

    def create_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead.
        
        Required params:
            - company_name: Company name
            - country: Country
            
        Optional params:
            - contact_name, contact_email, contact_phone, contact_title
            - website, category, source, search_keyword
            - discovery_path, sourcing_signal
            - product_interest, target_price, target_quantity
            - qualification_score, qualification_notes
            - created_by, first_seen_date
        """
        try:
            with get_db_session() as session:
                repo = LeadRepository(session)
                
                # Generate unique lead_id
                lead_id = f"lead_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Build lead object from params
                lead = Lead(
                    lead_id=lead_id,
                    company_name=params["company_name"],
                    country=params.get("country", "Unknown"),
                    website=params.get("website"),
                    category=params.get("category"),
                    source=params.get("source"),
                    search_keyword=params.get("search_keyword"),
                    discovery_path=params.get("discovery_path"),
                    sourcing_signal=params.get("sourcing_signal"),
                    contact_name=params.get("contact_name"),
                    contact_title=params.get("contact_title"),
                    contact_email=params.get("contact_email"),
                    contact_phone=params.get("contact_phone"),
                    contact_linkedin=params.get("contact_linkedin"),
                    product_interest=params.get("product_interest"),
                    target_price=params.get("target_price"),
                    target_quantity=params.get("target_quantity"),
                    status=params.get("status", "new"),
                    qualification_score=params.get("qualification_score"),
                    qualification_notes=params.get("qualification_notes"),
                    created_by=params.get("created_by"),
                    first_seen_date=params.get("first_seen_date"),
                    created_at=datetime.utcnow(),
                )
                
                created_lead = repo.create(lead)
                
                return {
                    "success": True,
                    "lead_id": created_lead.lead_id,
                    "data": self._lead_to_dict(created_lead)
                }
        except KeyError as e:
            return {"success": False, "error": f"Missing required field: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get lead details by lead_id.
        
        Required params:
            - lead_id: The unique lead identifier
        """
        try:
            lead_id = params.get("lead_id")
            if not lead_id:
                return {"success": False, "error": "Missing required field: lead_id"}
            
            with get_db_session() as session:
                repo = LeadRepository(session)
                lead = repo.get_by_lead_id(lead_id)
                
                if lead is None:
                    return {"success": False, "error": f"Lead not found: {lead_id}"}
                
                return {
                    "success": True,
                    "lead_id": lead.lead_id,
                    "data": self._lead_to_dict(lead)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing lead.
        
        Required params:
            - lead_id: The unique lead identifier
            
        Optional params:
            - Any Lead field to update (company_name, country, status, etc.)
        """
        try:
            lead_id = params.get("lead_id")
            if not lead_id:
                return {"success": False, "error": "Missing required field: lead_id"}
            
            with get_db_session() as session:
                repo = LeadRepository(session)
                lead = repo.get_by_lead_id(lead_id)
                
                if lead is None:
                    return {"success": False, "error": f"Lead not found: {lead_id}"}
                
                # Update allowed fields
                updatable_fields = [
                    "company_name", "website", "country", "category", "source",
                    "search_keyword", "discovery_path", "sourcing_signal",
                    "contact_name", "contact_title", "contact_email", 
                    "contact_phone", "contact_linkedin",
                    "product_interest", "target_price", "target_quantity",
                    "status", "qualification_score", "qualification_notes",
                    "created_by", "first_seen_date"
                ]
                
                updated_fields = {}
                for field in updatable_fields:
                    if field in params:
                        setattr(lead, field, params[field])
                        updated_fields[field] = params[field]
                
                lead.updated_at = datetime.utcnow()
                repo.update(lead)
                
                return {
                    "success": True,
                    "lead_id": lead.lead_id,
                    "updated_fields": updated_fields,
                    "updated_at": lead.updated_at.isoformat()
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_leads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all leads with optional filtering and pagination.
        
        Optional params:
            - page: Page number (default: 1)
            - per_page: Items per page (default: 20)
            - status: Filter by status (new, contacted, qualified, etc.)
            - country: Filter by country
        """
        try:
            page = max(1, params.get("page", 1))
            per_page = min(100, max(1, params.get("per_page", 20)))
            offset = (page - 1) * per_page
            status = params.get("status")
            country = params.get("country")
            
            with get_db_session() as session:
                repo = LeadRepository(session)
                
                if status:
                    leads = repo.get_by_status(status, offset=offset, limit=per_page)
                    total = len(repo.get_by_status(status, offset=0, limit=10000))
                elif country:
                    leads = repo.get_by_country(country, offset=offset, limit=per_page)
                    total = len(repo.get_by_country(country, offset=0, limit=10000))
                else:
                    leads = repo.get_all(offset=offset, limit=per_page)
                    total = repo.count()
                
                return {
                    "success": True,
                    "leads": [self._lead_to_dict(lead) for lead in leads],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": total
                    }
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a lead by lead_id.
        
        Required params:
            - lead_id: The unique lead identifier
        """
        try:
            lead_id = params.get("lead_id")
            if not lead_id:
                return {"success": False, "error": "Missing required field: lead_id"}
            
            with get_db_session() as session:
                repo = LeadRepository(session)
                lead = repo.get_by_lead_id(lead_id)
                
                if lead is None:
                    return {"success": False, "error": f"Lead not found: {lead_id}"}
                
                # Use internal id for deletion
                deleted = repo.delete(lead.id)
                
                if deleted:
                    return {
                        "success": True,
                        "lead_id": lead_id,
                        "deleted": True
                    }
                else:
                    return {"success": False, "error": "Failed to delete lead"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def qualify_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Qualify a lead with a score. Score must be >= 60."""
        lead_id = params.get("lead_id")
        if not lead_id:
            return {"success": False, "error": "Missing required field: lead_id"}

        score = params.get("qualification_score")
        if score is None:
            return {"success": False, "error": "Missing required field: qualification_score"}

        try:
            score = int(score)
        except (TypeError, ValueError):
            return {"success": False, "error": "qualification_score must be an integer"}

        if score < 60:
            return {"success": False, "error": "Score must be >= 60 to qualify a lead"}

        with get_db_session() as sess:
            repo = LeadRepository(sess)
            lead = repo.get_by_lead_id(lead_id)
            if not lead:
                return {"success": False, "error": f"Lead not found: {lead_id}"}
            if lead.status not in ("raw_lead", "new"):
                return {"success": False, "error": f"Cannot qualify lead with status: {lead.status}"}

            lead.status = "qualified"
            lead.qualification_score = score
            lead.qualification_notes = params.get("qualification_notes", "")
            sess.add(lead)

        return {"success": True, "lead_id": lead_id, "status": "qualified", "score": score}

    def reject_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reject a lead."""
        lead_id = params.get("lead_id")
        if not lead_id:
            return {"success": False, "error": "Missing required field: lead_id"}

        with get_db_session() as sess:
            repo = LeadRepository(sess)
            lead = repo.get_by_lead_id(lead_id)
            if not lead:
                return {"success": False, "error": f"Lead not found: {lead_id}"}
            lead.status = "rejected"
            sess.add(lead)

        return {"success": True, "lead_id": lead_id, "status": "rejected"}

    def convert_lead(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a lead to a customer.
        
        Required params:
            - lead_id: The unique lead identifier
            
        Optional params:
            - business_type: Customer business type
            - source_channel: Source channel for customer
            - notes: Additional notes
        """
        try:
            lead_id = params.get("lead_id")
            if not lead_id:
                return {"success": False, "error": "Missing required field: lead_id"}
            
            with get_db_session() as session:
                lead_repo = LeadRepository(session)
                customer_repo = CustomerRepository(session)
                
                lead = lead_repo.get_by_lead_id(lead_id)
                if lead is None:
                    return {"success": False, "error": f"Lead not found: {lead_id}"}
                
                # Generate customer_id
                customer_id = f"cust_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Create customer from lead data
                customer = Customer(
                    customer_id=customer_id,
                    company_name=lead.company_name,
                    website=lead.website,
                    country=lead.country,
                    business_type=params.get("business_type"),
                    source_channel=params.get("source_channel", lead.source),
                    notes=params.get("notes", lead.qualification_notes),
                    contact_status="new",
                    phone=lead.contact_phone,
                    created_at=datetime.utcnow(),
                )
                
                created_customer = customer_repo.create(customer)
                
                # Update lead status to converted
                lead.status = "converted"
                lead.updated_at = datetime.utcnow()
                lead_repo.update(lead)
                
                return {
                    "success": True,
                    "lead_id": lead_id,
                    "customer_id": created_customer.customer_id,
                    "converted_at": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_leads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search leads by various criteria.
        
        Optional params:
            - query: General search query (searches company_name, contact_name)
            - email: Search by contact email
            - country: Filter by country
            - status: Filter by status
            - page: Page number (default: 1)
            - per_page: Items per page (default: 20)
        """
        try:
            page = max(1, params.get("page", 1))
            per_page = min(100, max(1, params.get("per_page", 20)))
            offset = (page - 1) * per_page
            
            with get_db_session() as session:
                repo = LeadRepository(session)
                
                # If email is provided, use direct lookup
                if params.get("email"):
                    lead = repo.get_by_email(params["email"])
                    leads = [lead] if lead else []
                    total = 1 if lead else 0
                else:
                    # Filter by status and/or country
                    status = params.get("status")
                    country = params.get("country")
                    
                    if status and country:
                        leads = repo.get_by_status(status, offset=offset, limit=per_page)
                        leads = [l for l in leads if l.country == country]
                        total = len(leads)
                    elif status:
                        leads = repo.get_by_status(status, offset=offset, limit=per_page)
                        total = len(repo.get_by_status(status, offset=0, limit=10000))
                    elif country:
                        leads = repo.get_by_country(country, offset=offset, limit=per_page)
                        total = len(repo.get_by_country(country, offset=0, limit=10000))
                    else:
                        leads = repo.get_all(offset=offset, limit=per_page)
                        total = repo.count()
                
                return {
                    "success": True,
                    "leads": [self._lead_to_dict(lead) for lead in leads],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": total
                    }
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _lead_to_dict(self, lead: Lead) -> Dict[str, Any]:
        """Convert Lead model to dictionary."""
        return {
            "lead_id": lead.lead_id,
            "company_name": lead.company_name,
            "website": lead.website,
            "country": lead.country,
            "category": lead.category,
            "source": lead.source,
            "search_keyword": lead.search_keyword,
            "discovery_path": lead.discovery_path,
            "sourcing_signal": lead.sourcing_signal,
            "contact_name": lead.contact_name,
            "contact_title": lead.contact_title,
            "contact_email": lead.contact_email,
            "contact_phone": lead.contact_phone,
            "contact_linkedin": lead.contact_linkedin,
            "product_interest": lead.product_interest,
            "target_price": lead.target_price,
            "target_quantity": lead.target_quantity,
            "status": lead.status,
            "qualification_score": lead.qualification_score,
            "qualification_notes": lead.qualification_notes,
            "created_by": lead.created_by,
            "first_seen_date": lead.first_seen_date,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
        }
