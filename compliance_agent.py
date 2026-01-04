"""
Compliance Agent - Regulatory Safety Layer (Policy & Tax Enforcer)
Role: Validates tax calculations, applies jurisdiction rules,
      enforces company spend policies, flags compliance risks

NOTE: This agent uses AI for INTERPRETATION ONLY (not core functionality)
"""

from typing import Dict, List, Optional
from base_agent import BaseAgent, Invoice, InvoiceStatus

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ComplianceAgent(BaseAgent):
    """
    Regulatory safety layer that enforces compliance rules.
    Uses AI for interpretation only.
    """
    
    # Risk threshold constants (configurable)
    HIGH_VALUE_THRESHOLD = 50000
    ROUND_NUMBER_THRESHOLD = 1000
    
    def __init__(self, api_key: Optional[str] = None, 
                 high_value_threshold: float = 50000,
                 round_number_threshold: float = 1000):
        super().__init__("ComplianceAgent")
        
        # Configure thresholds
        self.HIGH_VALUE_THRESHOLD = high_value_threshold
        self.ROUND_NUMBER_THRESHOLD = round_number_threshold
        
        # Initialize AI for interpretation
        self.ai_enabled = False
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.ai_enabled = True
                self.logger.info("AI enabled for compliance interpretation")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI: {e}")
                
        # Tax rates by jurisdiction
        self.tax_rates = self._get_tax_rates()
        
        # Company spend policies
        self.spend_policies = self._get_spend_policies()
        
    def process(self, invoice: Invoice) -> Invoice:
        """
        Check invoice for compliance issues.
        
        Args:
            invoice: Invoice with extracted, validated, and matched data
            
        Returns:
            Invoice with compliance results
        """
        invoice.status = InvoiceStatus.COMPLIANCE_CHECK
        
        compliance_results = {
            "tax_valid": False,
            "jurisdiction_compliant": False,
            "policy_compliant": False,
            "risks": [],
            "warnings": [],
            "compliant": False
        }
        
        # 1. Validate tax calculations
        self._validate_tax(invoice.extracted_data, compliance_results)
        
        # 2. Apply jurisdiction rules
        self._check_jurisdiction(invoice.extracted_data, compliance_results)
        
        # 3. Enforce company spend policies
        self._enforce_policies(invoice.extracted_data, compliance_results)
        
        # 4. Flag compliance risks
        self._flag_risks(invoice.extracted_data, compliance_results)
        
        # Use AI for interpretation if there are edge cases
        if self.ai_enabled and (compliance_results["risks"] or compliance_results["warnings"]):
            interpretation = self._interpret_compliance_issues(invoice.extracted_data, compliance_results)
            compliance_results["ai_interpretation"] = interpretation
            
        # Determine overall compliance status
        compliance_results["compliant"] = (
            compliance_results["tax_valid"] and
            compliance_results["jurisdiction_compliant"] and
            compliance_results["policy_compliant"] and
            len(compliance_results["risks"]) == 0
        )
        
        # Store compliance results
        invoice.compliance_results = compliance_results
        
        # Update status
        if compliance_results["compliant"]:
            invoice.status = InvoiceStatus.COMPLIANT
            self.logger.info(f"Invoice {invoice.invoice_id} compliance check passed")
        else:
            invoice.status = InvoiceStatus.EXCEPTION
            invoice.add_warning(self.agent_name, f"Compliance issues: {compliance_results['risks']}")
            self.logger.warning(f"Invoice {invoice.invoice_id} compliance failed: {compliance_results['risks']}")
            
        # Add to audit trail
        invoice.add_audit_entry(
            self.agent_name,
            "compliance_check_completed",
            compliance_results
        )
        
        return invoice
        
    def _validate_tax(self, data: Dict, results: Dict):
        """Validate tax calculations"""
        subtotal = data.get("subtotal", 0)
        tax_amount = data.get("tax_amount", 0)
        
        # Extract state/jurisdiction from vendor address
        vendor_address = data.get("vendor_address", "")
        jurisdiction = self._extract_jurisdiction(vendor_address)
        
        expected_tax_rate = self.tax_rates.get(jurisdiction, 0.08)  # Default 8%
        expected_tax = subtotal * expected_tax_rate
        
        # Allow 1% tolerance for rounding
        tolerance = expected_tax * 0.01
        
        if abs(tax_amount - expected_tax) <= tolerance:
            results["tax_valid"] = True
        else:
            results["warnings"].append(
                f"Tax calculation mismatch: Expected {expected_tax:.2f} ({expected_tax_rate*100}%), "
                f"Got {tax_amount:.2f}"
            )
            results["tax_valid"] = False
            
    def _check_jurisdiction(self, data: Dict, results: Dict):
        """Check jurisdiction-specific rules"""
        vendor_address = data.get("vendor_address", "")
        jurisdiction = self._extract_jurisdiction(vendor_address)
        
        # Check if jurisdiction is supported
        if jurisdiction not in self.tax_rates:
            results["warnings"].append(f"Unknown jurisdiction: {jurisdiction}")
            results["jurisdiction_compliant"] = False
        else:
            results["jurisdiction_compliant"] = True
            
        # Check jurisdiction-specific requirements
        total_amount = data.get("total_amount", 0)
        
        # Example: Some jurisdictions require additional documentation for large amounts
        if jurisdiction == "CA" and total_amount > 10000:
            results["warnings"].append("CA jurisdiction: Amounts over $10,000 require additional documentation")
            
    def _enforce_policies(self, data: Dict, results: Dict):
        """Enforce company spend policies"""
        policy_violations = []
        
        total_amount = data.get("total_amount", 0)
        vendor = data.get("vendor_name", "")
        
        # Check against spend policies
        for policy in self.spend_policies:
            if policy["type"] == "max_amount":
                if total_amount > policy["limit"]:
                    policy_violations.append(
                        f"Exceeds maximum single invoice amount: ${total_amount} > ${policy['limit']}"
                    )
                    
            elif policy["type"] == "approved_vendor":
                if policy.get("enforce") and vendor not in policy.get("vendors", []):
                    policy_violations.append(
                        f"Vendor '{vendor}' not in approved vendor list"
                    )
                    
        if policy_violations:
            results["warnings"].extend(policy_violations)
            results["policy_compliant"] = False
        else:
            results["policy_compliant"] = True
            
    def _flag_risks(self, data: Dict, results: Dict):
        """Flag compliance risks"""
        risks = []
        
        # Check for unusual patterns
        total_amount = data.get("total_amount", 0)
        
        # Flag high-value invoices
        if total_amount > self.HIGH_VALUE_THRESHOLD:
            risks.append(f"High-value invoice: ${total_amount}")
            
        # Check for round numbers (potential fraud indicator)
        if total_amount > 0 and total_amount % self.ROUND_NUMBER_THRESHOLD == 0:
            risks.append(f"Round number invoice: ${total_amount} (potential fraud indicator)")
            
        # Check payment terms
        payment_terms = data.get("payment_terms", "")
        if "immediate" in payment_terms.lower() or "rush" in payment_terms.lower():
            risks.append("Urgent payment terms requested")
            
        results["risks"] = risks
        
    def _interpret_compliance_issues(self, data: Dict, results: Dict) -> str:
        """Use AI to interpret compliance issues"""
        try:
            prompt = f"""
Analyze these compliance issues for an invoice:

Invoice Data:
- Vendor: {data.get('vendor_name')}
- Amount: ${data.get('total_amount')}
- Tax: ${data.get('tax_amount')}

Compliance Results:
- Tax Valid: {results['tax_valid']}
- Jurisdiction Compliant: {results['jurisdiction_compliant']}
- Policy Compliant: {results['policy_compliant']}
- Risks: {results['risks']}
- Warnings: {results['warnings']}

Provide a brief interpretation of these compliance issues and recommend whether this invoice should:
1. Proceed with caution
2. Require manual review
3. Be rejected

Keep the response concise and actionable.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert compliance officer specializing in accounts payable and financial regulations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Compliance interpretation failed: {e}")
            return "Interpretation unavailable"
            
    def _extract_jurisdiction(self, address: str) -> str:
        """Extract jurisdiction (state) from address"""
        # Simple extraction - look for state abbreviations
        states = ["NY", "CA", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
        for state in states:
            if state in address:
                return state
        return "UNKNOWN"
        
    def _get_tax_rates(self) -> Dict[str, float]:
        """Get tax rates by jurisdiction"""
        return {
            "NY": 0.08875,  # New York
            "CA": 0.0725,   # California
            "TX": 0.0625,   # Texas
            "FL": 0.06,     # Florida
            "IL": 0.0625,   # Illinois
            "UNKNOWN": 0.08 # Default
        }
        
    def _get_spend_policies(self) -> List[Dict]:
        """Get company spend policies"""
        return [
            {
                "type": "max_amount",
                "limit": 100000,
                "description": "Single invoice cannot exceed $100,000"
            },
            {
                "type": "approved_vendor",
                "enforce": False,  # Warning only
                "vendors": ["Acme Corporation", "TechSupply Inc"],
                "description": "Prefer approved vendors"
            }
        ]
