"""
Database infrastructure module using SQLite and SQLModel.
Provides database session management and model definitions.
Maps to exact Excel field names from:
- 客户采集表 (Lead data)
- 客户开发表 (Customer data)
- 邮件记录表 (Email record data)
"""

import os
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlmodel.pool import StaticPool

# Database path — stored in data/ directory (gitignored)
DB_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DB_DIR, "foreign_trade.db")


class Lead(SQLModel, table=True):
    """Lead model - maps to 客户采集表 (Customer Collection Sheet)."""
    
    __tablename__ = "leads"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: str = Field(max_length=50, index=True)  # Excel: lead_id
    company_name: str = Field(max_length=255, index=True)  # Excel: Company Name
    website: Optional[str] = Field(default=None, max_length=500)  # Excel: Website
    country: str = Field(max_length=100, index=True)  # Excel: Country
    category: Optional[str] = Field(default=None, max_length=100)  # Excel: Category
    source: Optional[str] = Field(default=None, max_length=100)  # Excel: Source
    search_keyword: Optional[str] = Field(default=None, max_length=100)  # Excel: Search Keyword
    discovery_path: Optional[str] = Field(default=None, max_length=200)  # Excel: Discovery Path
    sourcing_signal: Optional[str] = Field(default=None)  # Excel: Sourcing Signal
    contact_name: Optional[str] = Field(default=None, max_length=100)  # Excel: Contact Name
    contact_title: Optional[str] = Field(default=None, max_length=100)  # Excel: Contact Title
    contact_email: Optional[str] = Field(default=None, max_length=255, index=True)  # Excel: Contact Email
    contact_phone: Optional[str] = Field(default=None, max_length=50)  # Excel: Contact Phone
    contact_linkedin: Optional[str] = Field(default=None, max_length=500)  # Excel: Contact LinkedIn
    product_interest: Optional[str] = Field(default=None)  # Excel: Product Interest
    target_price: Optional[str] = Field(default=None, max_length=50)  # Excel: Target Price
    target_quantity: Optional[str] = Field(default=None, max_length=50)  # Excel: Target Quantity
    status: str = Field(default="new", max_length=50, index=True)  # Excel: Status
    qualification_score: Optional[int] = Field(default=None)  # Excel: Qualification Score
    qualification_notes: Optional[str] = Field(default=None)  # Excel: Qualification Notes
    created_by: Optional[str] = Field(default=None, max_length=100)  # Excel: Created By
    first_seen_date: Optional[str] = Field(default=None, max_length=50)  # Excel: First Seen Date
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Excel: Created At
    updated_at: Optional[datetime] = Field(default=None)


class Customer(SQLModel, table=True):
    """Customer model - maps to 客户开发表 (Customer Development Sheet)."""
    
    __tablename__ = "customers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: str = Field(max_length=50, unique=True, index=True)  # Excel: customer_id
    company_name: str = Field(max_length=255, index=True)  # Excel: 公司名称
    website: Optional[str] = Field(default=None, max_length=500)  # Excel: 官网
    country: str = Field(max_length=100, index=True)  # Excel: 国家
    business_type: Optional[str] = Field(default=None, max_length=100)  # Excel: 业务类型
    source_channel: Optional[str] = Field(default=None, max_length=100)  # Excel: 来源渠道
    notes: Optional[str] = Field(default=None)  # Excel: 备注
    send_time_window: Optional[str] = Field(default=None, max_length=50)  # Excel: 发信时间
    contact_status: str = Field(default="new", max_length=50, index=True)  # Excel: 联系状态
    next_follow_up_date: Optional[str] = Field(default=None, max_length=50)  # Excel: 下次跟进日期
    follow_up_records: Optional[str] = Field(default=None)  # Excel: 跟进记录
    phone: Optional[str] = Field(default=None, max_length=50)  # Excel: 电话
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Excel: 创建时间
    updated_at: Optional[datetime] = Field(default=None)  # Excel: 更新时间


class EmailRecord(SQLModel, table=True):
    """EmailRecord model - maps to 邮件记录表 (Email Record Sheet)."""
    
    __tablename__ = "email_records"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: str = Field(max_length=50, index=True)  # Excel: customer_id
    company_name: str = Field(max_length=255)  # Excel: 公司名称
    contact_person: Optional[str] = Field(default=None, max_length=100)  # Excel: 联系人
    contact_title: Optional[str] = Field(default=None, max_length=100)  # Excel: 职位
    email: str = Field(max_length=255, index=True)  # Excel: 邮箱
    source: Optional[str] = Field(default=None, max_length=100)  # Excel: 来源
    status: str = Field(default="active", max_length=50, index=True)  # Excel: 状态
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Excel: 创建时间
    first_send_time: Optional[datetime] = Field(default=None)  # Excel: 第1次发送时间
    first_subject: Optional[str] = Field(default=None, max_length=500)  # Excel: 第1次主题
    first_send_status: Optional[str] = Field(default=None, max_length=50)  # Excel: 第1次状态
    sender_email: Optional[str] = Field(default=None, max_length=255)  # Excel: 发件邮箱
    phone: Optional[str] = Field(default=None, max_length=50)  # Excel: 电话
    remarks: Optional[str] = Field(default=None)  # Excel: 备注
    updated_at: Optional[datetime] = Field(default=None)


# Database engine setup
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def init_db():
    """Initialize the database, creating all tables."""
    SQLModel.metadata.create_all(engine)


def get_engine():
    """Get the shared database engine."""
    return engine


def get_session() -> Session:
    """Get a new database session."""
    return Session(engine)


@contextmanager
def get_db_session():
    """Context manager for database sessions with automatic commit/rollback."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Repository classes for each domain

class LeadRepository:
    """Repository for Lead domain operations (客户采集表)."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, lead: Lead) -> Lead:
        """Create a new lead."""
        self.session.add(lead)
        self.session.flush()
        return lead
    
    def get_by_id(self, lead_id: int) -> Optional[Lead]:
        """Get a lead by ID."""
        return self.session.get(Lead, lead_id)
    
    def get_by_lead_id(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by lead_id (Excel field)."""
        stmt = select(Lead).where(Lead.lead_id == lead_id)
        return self.session.exec(stmt).first()
    
    def get_all(self, offset: int = 0, limit: int = 20) -> list[Lead]:
        """Get all leads with pagination."""
        stmt = select(Lead).offset(offset).limit(limit).order_by(Lead.created_at.desc())
        return list(self.session.exec(stmt))
    
    def get_by_status(self, status: str, offset: int = 0, limit: int = 20) -> list[Lead]:
        """Get leads by status with pagination."""
        stmt = (
            select(Lead)
            .where(Lead.status == status)
            .offset(offset)
            .limit(limit)
            .order_by(Lead.created_at.desc())
        )
        return list(self.session.exec(stmt))
    
    def get_by_email(self, email: str) -> Optional[Lead]:
        """Get a lead by contact email address."""
        stmt = select(Lead).where(Lead.contact_email == email)
        return self.session.exec(stmt).first()
    
    def get_by_country(self, country: str, offset: int = 0, limit: int = 20) -> list[Lead]:
        """Get leads by country with pagination."""
        stmt = (
            select(Lead)
            .where(Lead.country == country)
            .offset(offset)
            .limit(limit)
            .order_by(Lead.created_at.desc())
        )
        return list(self.session.exec(stmt))
    
    def update(self, lead: Lead) -> Lead:
        """Update an existing lead."""
        lead.updated_at = datetime.utcnow()
        self.session.add(lead)
        self.session.flush()
        return lead
    
    def delete(self, lead_id: int) -> bool:
        """Delete a lead by ID."""
        lead = self.session.get(Lead, lead_id)
        if lead:
            self.session.delete(lead)
            self.session.flush()
            return True
        return False
    
    def count(self) -> int:
        """Count total leads."""
        return len(list(self.session.exec(select(Lead))))


class CustomerRepository:
    """Repository for Customer domain operations (客户开发表)."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, customer: Customer) -> Customer:
        """Create a new customer."""
        self.session.add(customer)
        self.session.flush()
        return customer
    
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        return self.session.get(Customer, customer_id)
    
    def get_by_customer_id(self, customer_id: str) -> Optional[Customer]:
        """Get a customer by customer_id (Excel field)."""
        stmt = select(Customer).where(Customer.customer_id == customer_id)
        return self.session.exec(stmt).first()
    
    def get_all(self, offset: int = 0, limit: int = 20, active_only: bool = True) -> list[Customer]:
        """Get all customers with pagination."""
        stmt = select(Customer)
        if active_only:
            stmt = stmt.where(Customer.contact_status != "deleted")
        stmt = stmt.offset(offset).limit(limit).order_by(Customer.created_at.desc())
        return list(self.session.exec(stmt))
    
    def get_by_email(self, email: str) -> Optional[Customer]:
        """Get a customer by contact email."""
        # Note: Customer doesn't have direct email field, check via EmailRecord
        stmt = select(Customer).where(Customer.company_name.contains(email.split('@')[1] if '@' in email else email))
        return self.session.exec(stmt).first()
    
    def get_by_country(self, country: str, offset: int = 0, limit: int = 20) -> list[Customer]:
        """Get customers by country with pagination."""
        stmt = (
            select(Customer)
            .where(Customer.country == country)
            .offset(offset)
            .limit(limit)
            .order_by(Customer.created_at.desc())
        )
        return list(self.session.exec(stmt))
    
    def get_by_contact_status(self, status: str, offset: int = 0, limit: int = 20) -> list[Customer]:
        """Get customers by contact status."""
        stmt = (
            select(Customer)
            .where(Customer.contact_status == status)
            .offset(offset)
            .limit(limit)
            .order_by(Customer.created_at.desc())
        )
        return list(self.session.exec(stmt))
    
    def update(self, customer: Customer) -> Customer:
        """Update an existing customer."""
        customer.updated_at = datetime.utcnow()
        self.session.add(customer)
        self.session.flush()
        return customer
    
    def delete(self, customer_id: int) -> bool:
        """Soft delete a customer by setting contact_status to deleted."""
        customer = self.session.get(Customer, customer_id)
        if customer:
            customer.contact_status = "deleted"
            customer.updated_at = datetime.utcnow()
            self.session.add(customer)
            self.session.flush()
            return True
        return False
    
    def count(self, active_only: bool = True) -> int:
        """Count total customers."""
        stmt = select(Customer)
        if active_only:
            stmt = stmt.where(Customer.contact_status != "deleted")
        return len(list(self.session.exec(stmt)))


class EmailRecordRepository:
    """Repository for EmailRecord domain operations (邮件记录表)."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, email_record: EmailRecord) -> EmailRecord:
        """Create a new email record."""
        self.session.add(email_record)
        self.session.flush()
        return email_record
    
    def get_by_id(self, email_id: int) -> Optional[EmailRecord]:
        """Get an email record by ID."""
        return self.session.get(EmailRecord, email_id)
    
    def get_by_customer_id(self, customer_id: str, offset: int = 0, limit: int = 20) -> list[EmailRecord]:
        """Get email records for a specific customer_id (Excel field)."""
        stmt = (
            select(EmailRecord)
            .where(EmailRecord.customer_id == customer_id)
            .offset(offset)
            .limit(limit)
            .order_by(EmailRecord.created_at.desc())
        )
        return list(self.session.exec(stmt))
    
    def get_by_email(self, email: str, offset: int = 0, limit: int = 20) -> list[EmailRecord]:
        """Get email records by recipient email address."""
        stmt = (
            select(EmailRecord)
            .where(EmailRecord.email == email)
            .offset(offset)
            .limit(limit)
            .order_by(EmailRecord.created_at.desc())
        )
        return list(self.session.exec(stmt))
    
    def get_by_status(self, status: str, offset: int = 0, limit: int = 20) -> list[EmailRecord]:
        """Get email records by status with pagination."""
        stmt = (
            select(EmailRecord)
            .where(EmailRecord.status == status)
            .offset(offset)
            .limit(limit)
            .order_by(EmailRecord.created_at.desc())
        )
        return list(self.session.exec(stmt))
    
    def get_by_send_status(self, send_status: str, offset: int = 0, limit: int = 20) -> list[EmailRecord]:
        """Get email records by first send status (第1次状态)."""
        stmt = (
            select(EmailRecord)
            .where(EmailRecord.first_send_status == send_status)
            .offset(offset)
            .limit(limit)
            .order_by(EmailRecord.created_at.desc())
        )
        return list(self.session.exec(stmt))
    
    def update(self, email_record: EmailRecord) -> EmailRecord:
        """Update an existing email record."""
        email_record.updated_at = datetime.utcnow()
        self.session.add(email_record)
        self.session.flush()
        return email_record
    
    def delete(self, email_id: int) -> bool:
        """Delete an email record by ID."""
        email_record = self.session.get(EmailRecord, email_id)
        if email_record:
            self.session.delete(email_record)
            self.session.flush()
            return True
        return False
    
    def count(self, customer_id: Optional[str] = None) -> int:
        """Count total email records, optionally filtered by customer_id."""
        stmt = select(EmailRecord)
        if customer_id:
            stmt = stmt.where(EmailRecord.customer_id == customer_id)
        return len(list(self.session.exec(stmt)))


# Convenience function to initialize database
def setup_database():
    """Initialize the database and create all tables."""
    init_db()
