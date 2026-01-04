"""
Posting Agent - System of Record Writer (ERP Operator)
Role: Posts invoice into ERP, applies correct GL coding,
      confirms posting success, handles retries safely

NOTE: This agent does NOT use AI - it's system integration only
"""

import time
from typing import Dict, Optional
from base_agent import BaseAgent, Invoice, InvoiceStatus


class PostingAgent(BaseAgent):
    """
    System of record writer that posts invoices to ERP.
    Uses direct system integration without AI.
    """
    
    def __init__(self, max_retries: int = 3):
        super().__init__("PostingAgent")
        
        # Retry configuration
        self.max_retries = max_retries
        self.retry_delay = 2  # seconds
        
        # GL account mapping
        self.gl_accounts = self._get_gl_mapping()
        
    def process(self, invoice: Invoice) -> Invoice:
        """
        Post invoice to ERP system.
        
        Args:
            invoice: Approved invoice ready for posting
            
        Returns:
            Invoice with posting results
        """
        # Only post approved invoices
        if invoice.status != InvoiceStatus.APPROVED:
            invoice.add_error(
                self.agent_name,
                f"Cannot post invoice with status: {invoice.status.value}"
            )
            return invoice
            
        invoice.status = InvoiceStatus.POSTING
        
        posting_results = {
            "posted": False,
            "erp_invoice_id": None,
            "gl_entries": [],
            "posting_timestamp": None,
            "attempts": 0,
            "errors": []
        }
        
        # Determine GL coding
        gl_entries = self._determine_gl_coding(invoice.extracted_data)
        posting_results["gl_entries"] = gl_entries
        
        # Attempt to post with retries
        success = False
        for attempt in range(1, self.max_retries + 1):
            posting_results["attempts"] = attempt
            
            try:
                # Post to ERP
                erp_invoice_id = self._post_to_erp(invoice, gl_entries)
                
                # Confirm posting
                if self._confirm_posting(erp_invoice_id):
                    posting_results["posted"] = True
                    posting_results["erp_invoice_id"] = erp_invoice_id
                    posting_results["posting_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    success = True
                    break
                else:
                    error_msg = f"Posting confirmation failed (attempt {attempt})"
                    posting_results["errors"].append(error_msg)
                    self.logger.warning(error_msg)
                    
            except (ConnectionError, TimeoutError) as e:
                # Network or timeout errors - retry
                error_msg = f"Network error on attempt {attempt}: {str(e)}"
                posting_results["errors"].append(error_msg)
                self.logger.error(error_msg)
            except ValueError as e:
                # Data validation errors - don't retry
                error_msg = f"Data validation error: {str(e)}"
                posting_results["errors"].append(error_msg)
                self.logger.error(error_msg)
                break  # Don't retry on data errors
            except Exception as e:
                error_msg = f"Posting attempt {attempt} failed: {str(e)}"
                posting_results["errors"].append(error_msg)
                self.logger.error(error_msg)
                
            # Wait before retry
            if attempt < self.max_retries:
                time.sleep(self.retry_delay)
                
        # Store posting results
        invoice.posting_results = posting_results
        
        # Update status
        if success:
            invoice.status = InvoiceStatus.POSTED
            self.logger.info(
                f"Invoice {invoice.invoice_id} posted successfully to ERP "
                f"as {posting_results['erp_invoice_id']}"
            )
        else:
            invoice.status = InvoiceStatus.FAILED
            invoice.add_error(
                self.agent_name,
                f"Failed to post invoice after {self.max_retries} attempts"
            )
            self.logger.error(f"Invoice {invoice.invoice_id} posting failed")
            
        # Add to audit trail
        invoice.add_audit_entry(
            self.agent_name,
            "posting_completed",
            posting_results
        )
        
        return invoice
        
    def _determine_gl_coding(self, invoice_data: Dict) -> list:
        """Determine appropriate GL accounts"""
        gl_entries = []
        
        vendor = invoice_data.get("vendor_name", "")
        line_items = invoice_data.get("line_items", [])
        
        # Get GL account based on vendor and line item type
        for item in line_items:
            description = item.get("description", "").lower()
            amount = item.get("total", 0)
            
            # Determine account based on description
            gl_account = self._get_gl_account(description)
            
            gl_entries.append({
                "account": gl_account,
                "description": item.get("description"),
                "debit": amount,
                "credit": 0
            })
            
        # Add accounts payable entry (credit)
        total = invoice_data.get("total_amount", 0)
        gl_entries.append({
            "account": "2000",  # Accounts Payable
            "description": f"AP - {vendor}",
            "debit": 0,
            "credit": total
        })
        
        return gl_entries
        
    def _get_gl_account(self, description: str) -> str:
        """Get GL account based on description"""
        description = description.lower()
        
        for keyword, account in self.gl_accounts.items():
            if keyword in description:
                return account
                
        # Default to general expense
        return "6000"
        
    def _post_to_erp(self, invoice: Invoice, gl_entries: list) -> str:
        """
        Post invoice to ERP system.
        
        Args:
            invoice: Invoice to post
            gl_entries: GL entries to post
            
        Returns:
            ERP invoice ID
        """
        # In a real system, this would make an API call to the ERP
        # For demo, we simulate the posting
        
        self.logger.info(f"Posting invoice {invoice.invoice_id} to ERP")
        self.logger.info(f"GL Entries: {gl_entries}")
        
        # Simulate ERP response
        erp_invoice_id = f"ERP-{invoice.invoice_id}"
        
        # Simulate some processing time
        time.sleep(0.5)
        
        return erp_invoice_id
        
    def _confirm_posting(self, erp_invoice_id: str) -> bool:
        """
        Confirm that invoice was successfully posted.
        
        Args:
            erp_invoice_id: ERP invoice ID to confirm
            
        Returns:
            True if posting confirmed, False otherwise
        """
        # In a real system, this would query the ERP to confirm
        # For demo, we simulate confirmation
        
        self.logger.info(f"Confirming posting of {erp_invoice_id}")
        
        # Simulate confirmation delay
        time.sleep(0.3)
        
        # Simulate successful confirmation
        return True
        
    def _get_gl_mapping(self) -> Dict[str, str]:
        """Get GL account mapping"""
        return {
            "service": "5000",      # Professional Services
            "supplies": "5100",     # Office Supplies
            "equipment": "1500",    # Equipment
            "software": "5200",     # Software/IT
            "travel": "6100",       # Travel & Entertainment
            "utilities": "6200",    # Utilities
            "rent": "6300",         # Rent
            "insurance": "6400"     # Insurance
        }
