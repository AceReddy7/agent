"""
Matching Agent - Financial Consistency Checker (PO & Contract Matcher)
Role: Matches invoice to PO/receipt, checks quantity, price, totals,
      applies tolerance rules, determines "clean" or "exception"

NOTE: This agent uses AI for EDGE CASES only (not core functionality)
"""

from typing import Dict, List, Optional, Any
from base_agent import BaseAgent, Invoice, InvoiceStatus

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class MatchingAgent(BaseAgent):
    """
    Financial consistency checker that matches invoices to POs/receipts.
    Uses AI for edge cases only.
    """
    
    def __init__(self, api_key: Optional[str] = None, tolerance: float = 0.05):
        super().__init__("MatchingAgent")
        
        # Price tolerance (5% by default)
        self.tolerance = tolerance
        
        # Initialize AI for edge cases
        self.ai_enabled = False
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.ai_enabled = True
                self.logger.info("AI enabled for edge case handling")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI: {e}")
                
        # Mock PO database (in production, this would be a real database)
        self.purchase_orders = self._get_mock_pos()
        
    def process(self, invoice: Invoice) -> Invoice:
        """
        Match invoice to PO and check financial consistency.
        
        Args:
            invoice: Invoice with extracted and validated data
            
        Returns:
            Invoice with matching results
        """
        invoice.status = InvoiceStatus.MATCHING
        
        matching_results = {
            "po_found": False,
            "po_number": None,
            "quantity_match": False,
            "price_match": False,
            "total_match": False,
            "within_tolerance": False,
            "match_type": "no_match",  # "exact", "within_tolerance", "exception"
            "issues": [],
            "is_clean": False
        }
        
        # Get PO number from invoice
        po_number = invoice.extracted_data.get("purchase_order_number")
        
        if not po_number:
            matching_results["issues"].append("No PO number found on invoice")
            matching_results["match_type"] = "exception"
        else:
            # Find matching PO
            po = self._find_purchase_order(po_number)
            
            if not po:
                matching_results["issues"].append(f"PO {po_number} not found in system")
                matching_results["match_type"] = "exception"
            else:
                matching_results["po_found"] = True
                matching_results["po_number"] = po_number
                
                # Perform matching checks
                self._check_quantities(invoice.extracted_data, po, matching_results)
                self._check_prices(invoice.extracted_data, po, matching_results)
                self._check_totals(invoice.extracted_data, po, matching_results)
                
                # Determine match type
                if matching_results["quantity_match"] and matching_results["price_match"] and matching_results["total_match"]:
                    matching_results["match_type"] = "exact"
                    matching_results["is_clean"] = True
                elif matching_results["within_tolerance"]:
                    matching_results["match_type"] = "within_tolerance"
                    matching_results["is_clean"] = True
                else:
                    matching_results["match_type"] = "exception"
                    # Use AI for edge case analysis only for complex or high-value cases
                    if self.ai_enabled and matching_results["issues"]:
                        # Only use AI for significant exceptions
                        if invoice.extracted_data.get("total_amount", 0) > 5000 or len(matching_results["issues"]) > 2:
                            edge_case_analysis = self._analyze_edge_case(invoice.extracted_data, po, matching_results)
                            matching_results["edge_case_analysis"] = edge_case_analysis
                        
        # Store matching results
        invoice.matching_results = matching_results
        
        # Update status
        if matching_results["is_clean"]:
            invoice.status = InvoiceStatus.MATCHED
            self.logger.info(f"Invoice {invoice.invoice_id} matched successfully: {matching_results['match_type']}")
        else:
            invoice.status = InvoiceStatus.EXCEPTION
            invoice.add_warning(self.agent_name, f"Matching exception: {matching_results['issues']}")
            self.logger.warning(f"Invoice {invoice.invoice_id} matching failed: {matching_results['issues']}")
            
        # Add to audit trail
        invoice.add_audit_entry(
            self.agent_name,
            "matching_completed",
            matching_results
        )
        
        return invoice
        
    def _find_purchase_order(self, po_number: str) -> Optional[Dict]:
        """Find PO in system"""
        return self.purchase_orders.get(po_number)
        
    def _check_quantities(self, invoice_data: Dict, po: Dict, results: Dict):
        """Check if quantities match"""
        invoice_items = invoice_data.get("line_items", [])
        po_items = po.get("line_items", [])
        
        if len(invoice_items) != len(po_items):
            results["issues"].append(f"Line item count mismatch: Invoice has {len(invoice_items)}, PO has {len(po_items)}")
            results["quantity_match"] = False
            return
            
        # Check each line item
        quantity_matches = True
        for inv_item, po_item in zip(invoice_items, po_items):
            inv_qty = inv_item.get("quantity", 0)
            po_qty = po_item.get("quantity", 0)
            
            if inv_qty != po_qty:
                results["issues"].append(f"Quantity mismatch for {inv_item.get('description')}: Invoice {inv_qty}, PO {po_qty}")
                quantity_matches = False
                
        results["quantity_match"] = quantity_matches
        
    def _check_prices(self, invoice_data: Dict, po: Dict, results: Dict):
        """Check if prices match within tolerance"""
        invoice_items = invoice_data.get("line_items", [])
        po_items = po.get("line_items", [])
        
        price_matches = True
        within_tolerance = True
        
        for inv_item, po_item in zip(invoice_items, po_items):
            inv_price = inv_item.get("unit_price", 0)
            po_price = po_item.get("unit_price", 0)
            
            # Check exact match
            if inv_price != po_price:
                price_matches = False
                
                # Check if within tolerance
                tolerance_amount = po_price * self.tolerance
                if abs(inv_price - po_price) > tolerance_amount:
                    results["issues"].append(f"Price exceeds tolerance for {inv_item.get('description')}: Invoice {inv_price}, PO {po_price}")
                    within_tolerance = False
                    
        results["price_match"] = price_matches
        results["within_tolerance"] = within_tolerance and not price_matches
        
    def _check_totals(self, invoice_data: Dict, po: Dict, results: Dict):
        """Check if totals match"""
        invoice_total = invoice_data.get("total_amount", 0)
        po_total = po.get("total_amount", 0)
        
        # Check exact match
        if abs(invoice_total - po_total) < 0.01:
            results["total_match"] = True
        else:
            # Check if within tolerance
            tolerance_amount = po_total * self.tolerance
            if abs(invoice_total - po_total) <= tolerance_amount:
                results["total_match"] = True
                results["within_tolerance"] = True
            else:
                results["issues"].append(f"Total amount mismatch: Invoice {invoice_total}, PO {po_total}")
                results["total_match"] = False
                
    def _analyze_edge_case(self, invoice_data: Dict, po: Dict, matching_results: Dict) -> str:
        """Use AI to analyze edge cases"""
        try:
            prompt = f"""
Analyze this invoice matching edge case:

Invoice Data:
{invoice_data}

Purchase Order:
{po}

Matching Issues:
{matching_results['issues']}

Determine if this is a legitimate exception that requires manual review or if it can be auto-approved with explanation.
Provide a brief analysis and recommendation.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert financial analyst specializing in invoice-to-PO matching edge cases."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Edge case analysis failed: {e}")
            return "Edge case analysis unavailable"
            
    def _get_mock_pos(self) -> Dict[str, Dict]:
        """Get mock purchase orders"""
        return {
            "PO-2024-001": {
                "po_number": "PO-2024-001",
                "vendor": "Acme Corporation",
                "total_amount": 1080.00,
                "line_items": [
                    {
                        "description": "Professional Services",
                        "quantity": 10,
                        "unit_price": 100.00,
                        "total": 1000.00
                    }
                ]
            }
        }
