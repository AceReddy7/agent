"""
Base Agent Framework for AI Accounts Payable Team
This module provides the foundational classes for all agents.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)


class InvoiceStatus(Enum):
    """Invoice processing status"""
    RECEIVED = "received"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    VALIDATING = "validating"
    VALIDATED = "validated"
    MATCHING = "matching"
    MATCHED = "matched"
    COMPLIANCE_CHECK = "compliance_check"
    COMPLIANT = "compliant"
    APPROVAL_PENDING = "approval_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTING = "posting"
    POSTED = "posted"
    FAILED = "failed"
    EXCEPTION = "exception"


class Invoice:
    """Invoice data model"""
    
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        self.status = InvoiceStatus.RECEIVED
        self.source = None
        self.timestamp = datetime.now()
        self.original_file = None
        self.extracted_data = {}
        self.validation_results = {}
        self.matching_results = {}
        self.compliance_results = {}
        self.approval_results = {}
        self.posting_results = {}
        self.audit_trail = []
        self.confidence_scores = {}
        self.errors = []
        self.warnings = []
        
    def add_audit_entry(self, agent: str, action: str, result: Any):
        """Add an entry to the audit trail"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "result": result,
            "status": self.status.value
        }
        self.audit_trail.append(entry)
        
    def add_error(self, agent: str, error: str):
        """Add an error to the invoice"""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "error": error
        })
        
    def add_warning(self, agent: str, warning: str):
        """Add a warning to the invoice"""
        self.warnings.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "warning": warning
        })
        
    def to_dict(self) -> Dict:
        """Convert invoice to dictionary"""
        return {
            "invoice_id": self.invoice_id,
            "status": self.status.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "original_file": self.original_file,
            "extracted_data": self.extracted_data,
            "validation_results": self.validation_results,
            "matching_results": self.matching_results,
            "compliance_results": self.compliance_results,
            "approval_results": self.approval_results,
            "posting_results": self.posting_results,
            "audit_trail": self.audit_trail,
            "confidence_scores": self.confidence_scores,
            "errors": self.errors,
            "warnings": self.warnings
        }


class BaseAgent(ABC):
    """Base class for all agents in the AP team"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(agent_name)
        self.next_agent = None
        self.metrics = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
    def set_next_agent(self, agent: 'BaseAgent'):
        """Set the next agent in the processing chain"""
        self.next_agent = agent
        
    @abstractmethod
    def process(self, invoice: Invoice) -> Invoice:
        """Process the invoice - must be implemented by subclasses"""
        pass
        
    def handle_and_pass(self, invoice: Invoice) -> Invoice:
        """Handle the invoice and pass to next agent"""
        try:
            self.logger.info(f"Processing invoice {invoice.invoice_id}")
            invoice = self.process(invoice)
            self.metrics["processed"] += 1
            self.metrics["successful"] += 1
            
            # Pass to next agent if exists
            if self.next_agent:
                return self.next_agent.handle_and_pass(invoice)
            
            return invoice
            
        except Exception as e:
            self.logger.error(f"Error processing invoice {invoice.invoice_id}: {str(e)}")
            invoice.add_error(self.agent_name, str(e))
            invoice.status = InvoiceStatus.FAILED
            self.metrics["failed"] += 1
            self.metrics["errors"].append({
                "invoice_id": invoice.invoice_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return invoice
            
    def get_metrics(self) -> Dict:
        """Get agent metrics"""
        return {
            "agent": self.agent_name,
            "metrics": self.metrics
        }
