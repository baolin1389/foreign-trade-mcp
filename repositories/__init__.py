"""Repositories module for data access layer."""

from .database import LeadRepository, CustomerRepository, EmailRecordRepository

__all__ = [
    "LeadRepository",
    "CustomerRepository",
    "EmailRecordRepository",
]
