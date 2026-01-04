# -*- coding: utf-8 -*-
"""
AI Accounts Payable Team - Main Orchestrator

This module orchestrates the entire AI AP team workflow.
It connects all agents in the processing pipeline and manages the invoice lifecycle.
"""

import os
from typing import Optional
from base_agent import Invoice
from intake_agent import IntakeAgent
from extraction_agent import ExtractionAgent
from validation_agent import ValidationAgent
from matching_agent import MatchingAgent
from compliance_agent import ComplianceAgent
from approvals_agent import ApprovalsAgent
from posting_agent import PostingAgent
from audit_agent import AuditAgent
from lead_agent import LeadAgent


class APTeamOrchestrator:
    """
    Main orchestrator for the AI Accounts Payable Team.
    Manages all agents and coordinates invoice processing.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the AP team with all agents.
        
        Args:
            openai_api_key: Optional OpenAI API key for AI-enabled features
        """
        # Get API key from environment if not provided
        if not openai_api_key:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            
        # Initialize all agents in the workflow
        self.intake_agent = IntakeAgent()
        self.extraction_agent = ExtractionAgent(api_key=openai_api_key)
        self.validation_agent = ValidationAgent()
        self.matching_agent = MatchingAgent(api_key=openai_api_key)
        self.compliance_agent = ComplianceAgent(api_key=openai_api_key)
        self.approvals_agent = ApprovalsAgent(api_key=openai_api_key)
        self.posting_agent = PostingAgent()
        self.audit_agent = AuditAgent(api_key=openai_api_key)
        
        # Initialize lead agent
        self.lead_agent = LeadAgent(api_key=openai_api_key)
        
        # Register all workers with lead agent
        self.lead_agent.register_agent(self.intake_agent)
        self.lead_agent.register_agent(self.extraction_agent)
        self.lead_agent.register_agent(self.validation_agent)
        self.lead_agent.register_agent(self.matching_agent)
        self.lead_agent.register_agent(self.compliance_agent)
        self.lead_agent.register_agent(self.approvals_agent)
        self.lead_agent.register_agent(self.posting_agent)
        self.lead_agent.register_agent(self.audit_agent)
        
        # Set up the processing chain
        self._setup_processing_chain()
        
        print("AI Accounts Payable Team initialized successfully!")
        print(f"AI features enabled: {self.extraction_agent.ai_enabled}")
        
    def _setup_processing_chain(self):
        """Set up the agent processing chain"""
        # Chain: Intake -> Extraction -> Validation -> Matching -> Compliance -> Approvals -> Posting -> Audit
        self.intake_agent.set_next_agent(self.extraction_agent)
        self.extraction_agent.set_next_agent(self.validation_agent)
        self.validation_agent.set_next_agent(self.matching_agent)
        self.matching_agent.set_next_agent(self.compliance_agent)
        self.compliance_agent.set_next_agent(self.approvals_agent)
        self.approvals_agent.set_next_agent(self.posting_agent)
        self.posting_agent.set_next_agent(self.audit_agent)
        
    def process_invoice(self, file_path: str, source: str = "upload") -> Invoice:
        """
        Process an invoice through the entire AP workflow.
        
        Args:
            file_path: Path to the invoice file
            source: Source of the invoice (e.g., 'upload', 'email', 'api')
            
        Returns:
            Fully processed invoice with complete audit trail
        """
        print(f"\n{'='*60}")
        print(f"Processing invoice from {source}: {file_path}")
        print(f"{'='*60}\n")
        
        # Step 1: Intake - receive the invoice
        invoice = self.intake_agent.receive_invoice(file_path, source)
        print(f"[OK] Invoice received: {invoice.invoice_id}")
        
        # Step 2: Process through the chain
        invoice = self.intake_agent.handle_and_pass(invoice)
        
        # Step 3: Update team metrics
        self.lead_agent.update_team_metrics(invoice)
        
        # Step 4: Print summary
        self._print_processing_summary(invoice)
        
        return invoice
        
    def _print_processing_summary(self, invoice: Invoice):
        """Print a summary of invoice processing"""
        print(f"\n{'='*60}")
        print(f"INVOICE PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Invoice ID: {invoice.invoice_id}")
        print(f"Final Status: {invoice.status.value}")
        print(f"")
        
        print(f"Processing Results:")
        print(f"  [OK] Extraction: {len(invoice.extracted_data)} fields extracted")
        print(f"  {'[OK]' if invoice.validation_results.get('passed') else '[X]'} Validation: {invoice.validation_results.get('passed', False)}")
        print(f"  {'[OK]' if invoice.matching_results.get('is_clean') else '[X]'} Matching: {invoice.matching_results.get('match_type', 'unknown')}")
        print(f"  {'[OK]' if invoice.compliance_results.get('compliant') else '[X]'} Compliance: {invoice.compliance_results.get('compliant', False)}")
        print(f"  {'[OK]' if invoice.approval_results.get('approval_decision') == 'approved' else '[X]'} Approval: {invoice.approval_results.get('approval_decision', 'unknown')}")
        print(f"  {'[OK]' if invoice.posting_results.get('posted') else '[X]'} Posting: {invoice.posting_results.get('posted', False)}")
        print(f"")
        
        if invoice.errors:
            print(f"Errors ({len(invoice.errors)}):")
            for error in invoice.errors:
                print(f"  - [{error['agent']}] {error['error']}")
            print(f"")
            
        if invoice.warnings:
            print(f"Warnings ({len(invoice.warnings)}):")
            for warning in invoice.warnings[:5]:  # Show first 5
                print(f"  - [{warning['agent']}] {warning['warning']}")
            print(f"")
            
        print(f"{'='*60}\n")
        
    def get_team_report(self) -> str:
        """
        Get comprehensive team performance report.
        
        Returns:
            Formatted team report
        """
        return self.lead_agent.generate_team_report()
        
    def monitor_team(self) -> dict:
        """
        Monitor team performance and detect issues.
        
        Returns:
            Monitoring report
        """
        return self.lead_agent.monitor_team()
        
    def get_sla_metrics(self) -> dict:
        """
        Get SLA performance metrics.
        
        Returns:
            SLA metrics
        """
        return self.audit_agent.get_sla_metrics()


def main():
    """Main entry point for testing"""
    print("AI Accounts Payable Team - Demo")
    print("=" * 60)
    
    # Initialize the team
    # Note: Set OPENAI_API_KEY environment variable to enable AI features
    orchestrator = APTeamOrchestrator()
    
    print("\nTeam initialized with the following agents:")
    print("1. Lead Agent - Manages all workers")
    print("2. Intake Agent - Receives invoices")
    print("3. Extraction Agent - Extracts data (AI-powered)")
    print("4. Validation Agent - Validates data")
    print("5. Matching Agent - Matches to POs (AI for edge cases)")
    print("6. Compliance Agent - Checks compliance (AI for interpretation)")
    print("7. Approvals Agent - Routes approvals (AI for risk scoring)")
    print("8. Posting Agent - Posts to ERP")
    print("9. Audit Agent - Maintains audit trail (AI for summaries)")
    
    print("\nTo process an invoice, use:")
    print("  orchestrator.process_invoice('path/to/invoice.pdf', 'upload')")
    print("\nTo get team report, use:")
    print("  orchestrator.get_team_report()")
    
    return orchestrator


if __name__ == "__main__":
    orchestrator = main()
