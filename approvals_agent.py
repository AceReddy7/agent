"""
Approvals Agent - Approval Logic Executor (Decision Router)
Role: Decides auto-approval vs escalation, routes to correct approver,
      enforces SLA timers, records approval decisions

NOTE: This agent uses AI for RISK SCORING only (not core functionality)
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from base_agent import BaseAgent, Invoice, InvoiceStatus

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ApprovalsAgent(BaseAgent):
    """
    Approval logic executor that routes invoices for approval.
    Uses AI for risk scoring only.
    """
    
    def __init__(self, api_key: Optional[str] = None, auto_approve_limit: float = 5000):
        super().__init__("ApprovalsAgent")
        
        # Auto-approval threshold
        self.auto_approve_limit = auto_approve_limit
        
        # SLA timer (in hours)
        self.sla_hours = 48
        
        # Initialize AI for risk scoring
        self.ai_enabled = False
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.ai_enabled = True
                self.logger.info("AI enabled for risk scoring")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI: {e}")
                
        # Approver hierarchy
        self.approvers = self._get_approver_hierarchy()
        
    def process(self, invoice: Invoice) -> Invoice:
        """
        Process invoice for approval.
        
        Args:
            invoice: Invoice with all prior checks completed
            
        Returns:
            Invoice with approval decision
        """
        invoice.status = InvoiceStatus.APPROVAL_PENDING
        
        approval_results = {
            "auto_approved": False,
            "requires_manual_approval": False,
            "approver": None,
            "approval_decision": None,  # "approved", "rejected", "pending"
            "risk_score": 0.0,
            "sla_deadline": None,
            "approval_notes": []
        }
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(invoice, approval_results)
        approval_results["risk_score"] = risk_score
        
        # Determine approval path
        total_amount = invoice.extracted_data.get("total_amount", 0)
        
        # Check if can be auto-approved
        can_auto_approve = self._can_auto_approve(invoice, total_amount, risk_score)
        
        if can_auto_approve:
            # Auto-approve
            approval_results["auto_approved"] = True
            approval_results["approval_decision"] = "approved"
            approval_results["approver"] = "SYSTEM"
            approval_results["approval_notes"].append("Auto-approved based on amount and risk score")
            invoice.status = InvoiceStatus.APPROVED
            self.logger.info(f"Invoice {invoice.invoice_id} auto-approved")
        else:
            # Route to manual approver
            approver = self._route_to_approver(total_amount, risk_score)
            approval_results["requires_manual_approval"] = True
            approval_results["approver"] = approver
            approval_results["approval_decision"] = "pending"
            
            # Set SLA deadline
            sla_deadline = datetime.now() + timedelta(hours=self.sla_hours)
            approval_results["sla_deadline"] = sla_deadline.isoformat()
            
            approval_results["approval_notes"].append(
                f"Routed to {approver} for manual approval. "
                f"SLA deadline: {sla_deadline.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # For demo purposes, simulate approval
            simulated_decision = self._simulate_approval(invoice, risk_score)
            approval_results["approval_decision"] = simulated_decision
            
            if simulated_decision == "approved":
                invoice.status = InvoiceStatus.APPROVED
                self.logger.info(f"Invoice {invoice.invoice_id} manually approved by {approver}")
            else:
                invoice.status = InvoiceStatus.REJECTED
                invoice.add_error(self.agent_name, f"Invoice rejected by {approver}")
                self.logger.warning(f"Invoice {invoice.invoice_id} rejected by {approver}")
                
        # Store approval results
        invoice.approval_results = approval_results
        
        # Add to audit trail
        invoice.add_audit_entry(
            self.agent_name,
            "approval_processed",
            approval_results
        )
        
        return invoice
        
    def _calculate_risk_score(self, invoice: Invoice, results: Dict) -> float:
        """
        Calculate risk score for the invoice.
        Uses AI for risk scoring.
        """
        risk_score = 0.0
        
        # Base risk factors
        total_amount = invoice.extracted_data.get("total_amount", 0)
        
        # Amount-based risk
        if total_amount > 50000:
            risk_score += 0.3
        elif total_amount > 10000:
            risk_score += 0.2
        elif total_amount > 5000:
            risk_score += 0.1
            
        # Validation issues
        if not invoice.validation_results.get("passed", False):
            risk_score += 0.2
            
        # Matching issues
        if not invoice.matching_results.get("is_clean", False):
            risk_score += 0.2
            
        # Compliance issues
        if not invoice.compliance_results.get("compliant", False):
            risk_score += 0.3
            
        # Cap at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Use AI for enhanced risk scoring if available
        if self.ai_enabled and risk_score > 0.3:
            ai_risk_adjustment = self._ai_risk_scoring(invoice)
            risk_score = (risk_score + ai_risk_adjustment) / 2
            results["approval_notes"].append(f"AI risk adjustment applied: {ai_risk_adjustment:.2f}")
            
        return round(risk_score, 2)
        
    def _ai_risk_scoring(self, invoice: Invoice) -> float:
        """Use AI to score risk"""
        try:
            prompt = f"""
Score the risk (0.0 to 1.0) for approving this invoice:

Invoice Details:
- Amount: ${invoice.extracted_data.get('total_amount', 0)}
- Vendor: {invoice.extracted_data.get('vendor_name')}
- Validation Passed: {invoice.validation_results.get('passed', False)}
- Matching Status: {invoice.matching_results.get('match_type', 'unknown')}
- Compliance: {invoice.compliance_results.get('compliant', False)}

Issues:
- Validation: {invoice.validation_results.get('issues', [])}
- Matching: {invoice.matching_results.get('issues', [])}
- Compliance Risks: {invoice.compliance_results.get('risks', [])}

Return only a number between 0.0 (no risk) and 1.0 (high risk).
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial risk assessment expert. Return only a numerical risk score between 0.0 and 1.0."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            score_text = response.choices[0].message.content.strip()
            
            # Validate and extract numeric score
            try:
                # Try to extract first number if response contains explanation
                import re
                numbers = re.findall(r'0\.\d+|1\.0|0', score_text)
                if numbers:
                    score = float(numbers[0])
                    # Ensure score is in valid range
                    return max(0.0, min(1.0, score))
                else:
                    # Try to parse the text directly
                    score = float(score_text)
                    return max(0.0, min(1.0, score))
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Invalid AI risk score format: {score_text}, error: {e}")
                return 0.5  # Default moderate risk
            
        except Exception as e:
            self.logger.error(f"AI risk scoring failed: {e}")
            return 0.5  # Default moderate risk
            
    def _can_auto_approve(self, invoice: Invoice, amount: float, risk_score: float) -> bool:
        """Determine if invoice can be auto-approved"""
        # Auto-approve if:
        # 1. Amount is below threshold
        # 2. Risk score is low
        # 3. All checks passed
        
        if amount > self.auto_approve_limit:
            return False
            
        if risk_score > 0.3:
            return False
            
        # Check that all validations passed
        if not invoice.validation_results.get("passed", False):
            return False
            
        if not invoice.matching_results.get("is_clean", False):
            return False
            
        if not invoice.compliance_results.get("compliant", False):
            return False
            
        return True
        
    def _route_to_approver(self, amount: float, risk_score: float) -> str:
        """Route invoice to appropriate approver"""
        # Route based on amount and risk
        
        if amount > 50000 or risk_score > 0.7:
            return self.approvers["senior_manager"]
        elif amount > 10000 or risk_score > 0.5:
            return self.approvers["manager"]
        else:
            return self.approvers["supervisor"]
            
    def _simulate_approval(self, invoice: Invoice, risk_score: float) -> str:
        """Simulate manual approval decision (for demo)"""
        # In a real system, this would wait for actual human approval
        
        # For demo: auto-approve if risk is moderate or low
        if risk_score < 0.7:
            return "approved"
        else:
            return "rejected"
            
    def _get_approver_hierarchy(self) -> Dict[str, str]:
        """Get approver hierarchy"""
        return {
            "supervisor": "John Supervisor",
            "manager": "Jane Manager",
            "senior_manager": "Bob Senior Manager"
        }
