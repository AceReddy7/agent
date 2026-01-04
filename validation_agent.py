"""
Validation Agent - First Quality Gate / Sanity Checker
Role: Validates vendor against master data, detects duplicates,
      checks required fields, flags inconsistencies

NOTE: This agent does NOT use AI - it's rules-based validation
"""

from typing import Dict, List, Set
from datetime import datetime
from base_agent import BaseAgent, Invoice, InvoiceStatus


class ValidationAgent(BaseAgent):
    """
    First quality gate that performs sanity checks on invoices.
    Uses rules-based validation without AI.
    """
    
    def __init__(self, master_vendors: List[str] = None):
        super().__init__("ValidationAgent")
        
        # Master vendor list (in production, this would come from a database)
        self.master_vendors = set(master_vendors) if master_vendors else self._get_default_vendors()
        
        # Track processed invoices for duplicate detection
        self.processed_invoice_numbers: Set[str] = set()
        
        # Required fields for an invoice
        self.required_fields = [
            "vendor_name",
            "invoice_number",
            "invoice_date",
            "total_amount"
        ]
        
    def process(self, invoice: Invoice) -> Invoice:
        """
        Validate invoice data.
        
        Args:
            invoice: Invoice with extracted data
            
        Returns:
            Validated invoice with validation results
        """
        invoice.status = InvoiceStatus.VALIDATING
        
        validation_results = {
            "vendor_valid": False,
            "no_duplicates": False,
            "required_fields_present": False,
            "data_consistent": False,
            "issues": [],
            "passed": False
        }
        
        # 1. Validate vendor against master data
        vendor_valid = self._validate_vendor(invoice.extracted_data, validation_results)
        
        # 2. Detect duplicates
        no_duplicates = self._check_duplicates(invoice.extracted_data, validation_results)
        
        # 3. Check required fields
        required_fields_ok = self._check_required_fields(invoice.extracted_data, validation_results)
        
        # 4. Flag inconsistencies
        data_consistent = self._check_consistency(invoice.extracted_data, validation_results)
        
        # Determine overall validation status
        validation_results["passed"] = (
            vendor_valid and 
            no_duplicates and 
            required_fields_ok and 
            data_consistent
        )
        
        # Store validation results
        invoice.validation_results = validation_results
        
        # Update status
        if validation_results["passed"]:
            invoice.status = InvoiceStatus.VALIDATED
            self.logger.info(f"Invoice {invoice.invoice_id} validation passed")
        else:
            invoice.status = InvoiceStatus.EXCEPTION
            invoice.add_warning(self.agent_name, f"Validation failed: {validation_results['issues']}")
            self.logger.warning(f"Invoice {invoice.invoice_id} validation failed: {validation_results['issues']}")
        
        # Add to audit trail
        invoice.add_audit_entry(
            self.agent_name,
            "validation_completed",
            validation_results
        )
        
        return invoice
        
    def _validate_vendor(self, data: Dict, results: Dict) -> bool:
        """Validate vendor against master data"""
        vendor_name = data.get("vendor_name", "")
        
        if not vendor_name:
            results["issues"].append("Vendor name missing")
            return False
            
        # Check against master vendor list
        if vendor_name not in self.master_vendors:
            results["issues"].append(f"Vendor '{vendor_name}' not in master data")
            results["vendor_valid"] = False
            return False
            
        results["vendor_valid"] = True
        return True
        
    def _check_duplicates(self, data: Dict, results: Dict) -> bool:
        """Detect duplicate invoices"""
        invoice_number = data.get("invoice_number", "")
        
        if not invoice_number:
            results["issues"].append("Invoice number missing for duplicate check")
            return False
            
        # Check if invoice number already processed
        if invoice_number in self.processed_invoice_numbers:
            results["issues"].append(f"Duplicate invoice number: {invoice_number}")
            results["no_duplicates"] = False
            return False
            
        # Add to processed set
        self.processed_invoice_numbers.add(invoice_number)
        results["no_duplicates"] = True
        return True
        
    def _check_required_fields(self, data: Dict, results: Dict) -> bool:
        """Check that all required fields are present"""
        missing_fields = []
        
        for field in self.required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
                
        if missing_fields:
            results["issues"].append(f"Missing required fields: {missing_fields}")
            results["required_fields_present"] = False
            return False
            
        results["required_fields_present"] = True
        return True
        
    def _check_consistency(self, data: Dict, results: Dict) -> bool:
        """Flag data inconsistencies"""
        issues = []
        
        # Check if total = subtotal + tax
        subtotal = data.get("subtotal", 0)
        tax = data.get("tax_amount", 0)
        total = data.get("total_amount", 0)
        
        if subtotal and tax and total:
            calculated_total = subtotal + tax
            # Allow small rounding differences
            if abs(calculated_total - total) > 0.01:
                issues.append(f"Total amount mismatch: {total} != {subtotal} + {tax}")
                
        # Check if line items sum to subtotal
        line_items = data.get("line_items", [])
        if line_items:
            line_items_total = sum(item.get("total", 0) for item in line_items)
            if subtotal and abs(line_items_total - subtotal) > 0.01:
                issues.append(f"Line items total mismatch: {line_items_total} != {subtotal}")
                
        # Check date logic (invoice date should be before due date)
        invoice_date = data.get("invoice_date")
        due_date = data.get("due_date")
        
        if invoice_date and due_date:
            try:
                inv_date = datetime.strptime(invoice_date, "%Y-%m-%d")
                d_date = datetime.strptime(due_date, "%Y-%m-%d")
                if inv_date > d_date:
                    issues.append(f"Invoice date {invoice_date} is after due date {due_date}")
            except ValueError:
                issues.append("Invalid date format")
                
        if issues:
            results["issues"].extend(issues)
            results["data_consistent"] = False
            return False
            
        results["data_consistent"] = True
        return True
        
    def _get_default_vendors(self) -> Set[str]:
        """Get default master vendor list"""
        return {
            "Acme Corporation",
            "TechSupply Inc",
            "Office Depot",
            "Global Services Ltd",
            "Premier Solutions"
        }
