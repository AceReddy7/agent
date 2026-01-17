"""
Intake Agent - Entry Point Worker
Role: Receives invoices (upload/API), assigns unique invoice ID, 
      records source & timestamp, stores original invoice immutably,
      hands off to Extraction Agent

NOTE: This agent does NOT use AI - it's purely workflow-based
"""

import uuid
import os
import shutil
from datetime import datetime
from typing import Dict, Any
from base_agent import BaseAgent, Invoice, InvoiceStatus


class IntakeAgent(BaseAgent):
    """
    Entry point worker for invoice processing.
    Handles invoice ingestion without AI capabilities.
    """
    
    def __init__(self, storage_path: str = "./invoices"):
        super().__init__("IntakeAgent")
        self.storage_path = storage_path
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
            
    def receive_invoice(self, file_path: str, source: str) -> Invoice:
        """
        Receive an invoice from external source.
        
        Args:
            file_path: Path to the invoice file
            source: Source of the invoice (e.g., 'email', 'api', 'upload')
            
        Returns:
            Invoice object with unique ID
        """
        # Generate unique invoice ID
        invoice_id = self._generate_invoice_id()
        
        # Create invoice object
        invoice = Invoice(invoice_id)
        invoice.source = source
        invoice.timestamp = datetime.now()
        
        # Store original file immutably
        stored_file_path = self._store_invoice_file(invoice_id, file_path)
        invoice.original_file = stored_file_path
        
        # Record in audit trail
        invoice.add_audit_entry(
            self.agent_name,
            "invoice_received",
            {
                "invoice_id": invoice_id,
                "source": source,
                "timestamp": invoice.timestamp.isoformat(),
                "file_path": stored_file_path
            }
        )
        
        self.logger.info(f"Invoice {invoice_id} received from {source}")
        
        return invoice
        
    def process(self, invoice: Invoice) -> Invoice:
        """
        Process the invoice (already received).
        This is called when invoice is passed through the chain.
        
        Args:
            invoice: Invoice object
            
        Returns:
            Processed invoice
        """
        # Update status
        invoice.status = InvoiceStatus.RECEIVED
        
        # Add processing record
        invoice.add_audit_entry(
            self.agent_name,
            "intake_completed",
            {
                "invoice_id": invoice.invoice_id,
                "ready_for_extraction": True
            }
        )
        
        self.logger.info(f"Invoice {invoice.invoice_id} intake completed, ready for extraction")
        
        return invoice
        
    def _generate_invoice_id(self) -> str:
        """Generate a unique invoice ID"""
        # Format: INV-YYYYMMDD-UUID
        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8]
        return f"INV-{date_str}-{unique_id}"
        
    def _store_invoice_file(self, invoice_id: str, source_file: str) -> str:
        """
        Store invoice file immutably.
        
        Args:
            invoice_id: Unique invoice ID
            source_file: Path to source file
            
        Returns:
            Path to stored file
        """
        # Get file extension
        _, ext = os.path.splitext(source_file)
        
        # Create storage path
        stored_file = os.path.join(self.storage_path, f"{invoice_id}{ext}")
        
        # Copy file (immutable storage)
        shutil.copy2(source_file, stored_file)
        
        # Make file read-only
        os.chmod(stored_file, 0o444)
        
        self.logger.info(f"Invoice file stored at {stored_file}")
        
        return stored_file
