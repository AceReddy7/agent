"""
Audit Agent - Continuous Oversight (Observer)
Role: Builds full audit trail per invoice, tracks errors & anomalies,
      monitors SLA performance, generates audit-ready reports

NOTE: This agent uses AI for SUMMARIES only (not core functionality)
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from base_agent import BaseAgent, Invoice, InvoiceStatus

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AuditAgent(BaseAgent):
    """
    Continuous oversight agent that maintains audit trails.
    Uses AI for summaries only.
    """
    
    def __init__(self, api_key: Optional[str] = None, audit_path: str = "./audit_trails"):
        super().__init__("AuditAgent")
        
        # Initialize AI for summaries
        self.ai_enabled = False
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.ai_enabled = True
                self.logger.info("AI enabled for audit summaries")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI: {e}")
                
        self.audit_path = audit_path
        
        # SLA tracking
        self.sla_metrics = {
            "total_invoices": 0,
            "within_sla": 0,
            "sla_breaches": 0,
            "average_processing_time": 0
        }
        
    def process(self, invoice: Invoice) -> Invoice:
        """
        Build comprehensive audit trail for invoice.
        
        Args:
            invoice: Processed invoice
            
        Returns:
            Invoice with complete audit trail
        """
        # Build full audit trail
        audit_report = self._build_audit_trail(invoice)
        
        # Track errors and anomalies
        self._track_errors_and_anomalies(invoice, audit_report)
        
        # Monitor SLA performance
        self._monitor_sla(invoice, audit_report)
        
        # Generate AI summary if enabled
        if self.ai_enabled:
            summary = self._generate_ai_summary(invoice, audit_report)
            audit_report["ai_summary"] = summary
            
        # Save audit report
        self._save_audit_report(invoice.invoice_id, audit_report)
        
        # Add final audit entry
        invoice.add_audit_entry(
            self.agent_name,
            "audit_completed",
            {
                "audit_report_generated": True,
                "total_errors": len(invoice.errors),
                "total_warnings": len(invoice.warnings),
                "final_status": invoice.status.value
            }
        )
        
        self.logger.info(f"Audit trail completed for invoice {invoice.invoice_id}")
        
        return invoice
        
    def _build_audit_trail(self, invoice: Invoice) -> Dict:
        """Build comprehensive audit trail"""
        processing_time = (datetime.now() - invoice.timestamp).total_seconds()
        
        audit_report = {
            "invoice_id": invoice.invoice_id,
            "audit_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": processing_time,
            "final_status": invoice.status.value,
            "source": invoice.source,
            "received_timestamp": invoice.timestamp.isoformat(),
            
            # Agent activities
            "agent_activities": invoice.audit_trail,
            
            # Results by stage
            "extraction_results": {
                "data": invoice.extracted_data,
                "confidence_scores": invoice.confidence_scores
            },
            "validation_results": invoice.validation_results,
            "matching_results": invoice.matching_results,
            "compliance_results": invoice.compliance_results,
            "approval_results": invoice.approval_results,
            "posting_results": invoice.posting_results,
            
            # Issues
            "errors": invoice.errors,
            "warnings": invoice.warnings,
            
            # Metrics
            "error_count": len(invoice.errors),
            "warning_count": len(invoice.warnings),
            "agent_count": len(set(entry["agent"] for entry in invoice.audit_trail))
        }
        
        return audit_report
        
    def _track_errors_and_anomalies(self, invoice: Invoice, audit_report: Dict):
        """Track and categorize errors and anomalies"""
        anomalies = []
        
        # Check for validation anomalies
        if not invoice.validation_results.get("passed", False):
            anomalies.append({
                "type": "validation_failure",
                "severity": "high",
                "details": invoice.validation_results.get("issues", [])
            })
            
        # Check for matching anomalies
        if invoice.matching_results.get("match_type") == "exception":
            anomalies.append({
                "type": "matching_exception",
                "severity": "medium",
                "details": invoice.matching_results.get("issues", [])
            })
            
        # Check for compliance risks
        if invoice.compliance_results.get("risks"):
            anomalies.append({
                "type": "compliance_risk",
                "severity": "high",
                "details": invoice.compliance_results.get("risks", [])
            })
            
        # Check for high-risk approvals
        risk_score = invoice.approval_results.get("risk_score", 0)
        if risk_score > 0.7:
            anomalies.append({
                "type": "high_risk_approval",
                "severity": "high",
                "details": f"Risk score: {risk_score}"
            })
            
        # Check for posting failures
        if not invoice.posting_results.get("posted", False):
            anomalies.append({
                "type": "posting_failure",
                "severity": "critical",
                "details": invoice.posting_results.get("errors", [])
            })
            
        audit_report["anomalies"] = anomalies
        audit_report["anomaly_count"] = len(anomalies)
        
    def _monitor_sla(self, invoice: Invoice, audit_report: Dict):
        """Monitor SLA performance"""
        processing_time = audit_report["processing_time_seconds"]
        
        # SLA target: 24 hours (86400 seconds)
        sla_target = 86400
        
        within_sla = processing_time <= sla_target
        
        # Update SLA metrics
        self.sla_metrics["total_invoices"] += 1
        if within_sla:
            self.sla_metrics["within_sla"] += 1
        else:
            self.sla_metrics["sla_breaches"] += 1
            
        # Calculate average processing time
        total = self.sla_metrics["total_invoices"]
        current_avg = self.sla_metrics["average_processing_time"]
        self.sla_metrics["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        audit_report["sla_performance"] = {
            "processing_time_seconds": processing_time,
            "sla_target_seconds": sla_target,
            "within_sla": within_sla,
            "sla_compliance_percentage": (
                self.sla_metrics["within_sla"] / self.sla_metrics["total_invoices"] * 100
            )
        }
        
    def _generate_ai_summary(self, invoice: Invoice, audit_report: Dict) -> str:
        """Generate AI-powered audit summary"""
        try:
            prompt = f"""
Generate a concise audit summary for this invoice processing:

Invoice ID: {invoice.invoice_id}
Status: {invoice.status.value}
Processing Time: {audit_report['processing_time_seconds']:.1f} seconds

Results:
- Validation: {"Passed" if invoice.validation_results.get('passed') else "Failed"}
- Matching: {invoice.matching_results.get('match_type', 'unknown')}
- Compliance: {"Compliant" if invoice.compliance_results.get('compliant') else "Non-compliant"}
- Approval: {invoice.approval_results.get('approval_decision', 'unknown')}
- Posted: {"Yes" if invoice.posting_results.get('posted') else "No"}

Errors: {len(invoice.errors)}
Warnings: {len(invoice.warnings)}
Anomalies: {audit_report.get('anomaly_count', 0)}

Provide a brief 2-3 sentence summary suitable for an audit report.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert auditor. Provide concise, professional audit summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"AI summary generation failed: {e}")
            return "Summary generation unavailable"
            
    def _save_audit_report(self, invoice_id: str, audit_report: Dict):
        """Save audit report to file"""
        import os
        
        # Create audit directory if it doesn't exist
        if not os.path.exists(self.audit_path):
            os.makedirs(self.audit_path)
            
        # Save report as JSON
        report_file = os.path.join(self.audit_path, f"{invoice_id}_audit.json")
        
        with open(report_file, 'w') as f:
            json.dump(audit_report, f, indent=2)
            
        self.logger.info(f"Audit report saved to {report_file}")
        
    def get_sla_metrics(self) -> Dict:
        """Get overall SLA metrics"""
        return self.sla_metrics
        
    def generate_audit_ready_report(self) -> str:
        """Generate comprehensive audit-ready report"""
        report = f"""
=== AUDIT REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SLA Performance:
- Total Invoices Processed: {self.sla_metrics['total_invoices']}
- Within SLA: {self.sla_metrics['within_sla']}
- SLA Breaches: {self.sla_metrics['sla_breaches']}
- SLA Compliance Rate: {(self.sla_metrics['within_sla'] / max(self.sla_metrics['total_invoices'], 1) * 100):.1f}%
- Average Processing Time: {self.sla_metrics['average_processing_time']:.1f} seconds

Agent Performance:
{self._format_agent_metrics()}

"""
        return report
        
    def _format_agent_metrics(self) -> str:
        """Format agent metrics for report"""
        return f"- {self.agent_name}: {self.metrics['processed']} processed, {self.metrics['successful']} successful, {self.metrics['failed']} failed"
