# -*- coding: utf-8 -*-
"""
Example Usage of AI Accounts Payable Team

This script demonstrates how to use the AP team to process invoices.
"""

import json
from ap_team_orchestrator import APTeamOrchestrator


def create_sample_invoice():
    """Create a sample invoice file for testing"""
    import os
    
    # Create sample invoices directory
    if not os.path.exists("sample_invoices"):
        os.makedirs("sample_invoices")
        
    # Sample invoice data
    invoice_data = """
INVOICE

Acme Corporation
123 Business St, Suite 100
New York, NY 10001

Invoice Number: INV-2024-0001
Invoice Date: 2024-01-15
Due Date: 2024-02-15
Purchase Order: PO-2024-0001

Bill To:
Your Company
456 Main Street
Anytown, CA 90001

ITEM DESCRIPTION                QTY    UNIT PRICE    TOTAL
Professional Services            10     $100.00      $1,000.00

                                        Subtotal:    $1,000.00
                                        Tax (8%):       $80.00
                                        TOTAL:       $1,080.00

Payment Terms: Net 30
"""
    
    # Save to file
    invoice_file = "sample_invoices/invoice_001.txt"
    with open(invoice_file, 'w') as f:
        f.write(invoice_data)
        
    print(f"Sample invoice created: {invoice_file}")
    return invoice_file


def example_1_basic_processing():
    """Example 1: Basic invoice processing"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Invoice Processing")
    print("="*60)
    
    # Initialize the AP team
    orchestrator = APTeamOrchestrator()
    
    # Create a sample invoice
    invoice_file = create_sample_invoice()
    
    # Process the invoice
    invoice = orchestrator.process_invoice(invoice_file, source="upload")
    
    # Print invoice details
    print("\nInvoice Details:")
    print(json.dumps(invoice.to_dict(), indent=2, default=str))
    
    return orchestrator, invoice


def example_2_team_monitoring():
    """Example 2: Team monitoring and reporting"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Team Monitoring and Reporting")
    print("="*60)
    
    # Initialize the AP team
    orchestrator = APTeamOrchestrator()
    
    # Process multiple invoices
    invoice_file = create_sample_invoice()
    
    print("\nProcessing multiple invoices...")
    for i in range(3):
        orchestrator.process_invoice(invoice_file, source=f"batch_{i}")
        
    # Get team report
    print("\n" + orchestrator.get_team_report())
    
    # Get SLA metrics
    print("\nSLA Metrics:")
    print(json.dumps(orchestrator.get_sla_metrics(), indent=2))
    
    # Monitor team
    print("\nTeam Monitoring Report:")
    monitoring_report = orchestrator.monitor_team()
    print(json.dumps(monitoring_report, indent=2, default=str))
    
    return orchestrator


def example_3_agent_roles():
    """Example 3: Demonstrate each agent's specific role"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Agent Roles and Responsibilities")
    print("="*60)
    
    print("""
Agent Role Summary (with AI usage as specified):

1. Lead Agent (Pattern Detection Only)
   - Manages all 8 workers
   - Monitors performance
   - Detects bottlenecks/failures
   - Re-routes workloads
   - Escalates issues
   - Produces team reports
   AI: Pattern detection in team performance

2. Intake Agent (NO AI)
   - Receives invoices
   - Assigns unique IDs
   - Records source & timestamp
   - Stores immutably
   - Hands off to Extraction

3. Extraction Agent (CORE AI)
   - Reads PDFs/images
   - Extracts all invoice fields
   - Produces structured JSON
   - Assigns confidence scores
   AI: Core data extraction functionality

4. Validation Agent (NO AI)
   - Validates vendor against master data
   - Detects duplicates
   - Checks required fields
   - Flags inconsistencies

5. Matching Agent (Edge Cases Only)
   - Matches to PO/receipt
   - Checks quantities, prices, totals
   - Applies tolerance rules
   - Determines clean vs exception
   AI: Edge case analysis only

6. Compliance Agent (Interpretation Only)
   - Validates tax calculations
   - Applies jurisdiction rules
   - Enforces spend policies
   - Flags compliance risks
   AI: Interpretation of compliance issues only

7. Approvals Agent (Risk Scoring Only)
   - Decides auto-approval vs escalation
   - Routes to correct approver
   - Enforces SLA timers
   - Records decisions
   AI: Risk scoring only

8. Posting Agent (NO AI)
   - Posts to ERP
   - Applies GL coding
   - Confirms success
   - Handles retries

9. Audit Agent (Summaries Only)
   - Builds audit trail
   - Tracks errors & anomalies
   - Monitors SLA
   - Generates reports
   AI: Audit summaries only
""")


def example_4_workflow():
    """Example 4: Complete workflow demonstration"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Complete Workflow")
    print("="*60)
    
    orchestrator = APTeamOrchestrator()
    invoice_file = create_sample_invoice()
    
    print("\nWorkflow Steps:")
    print("1. Invoice received → Intake Agent")
    print("2. Data extracted → Extraction Agent (AI)")
    print("3. Data validated → Validation Agent")
    print("4. Matched to PO → Matching Agent (AI for edge cases)")
    print("5. Compliance checked → Compliance Agent (AI for interpretation)")
    print("6. Approval routed → Approvals Agent (AI for risk scoring)")
    print("7. Posted to ERP → Posting Agent")
    print("8. Audit trail created → Audit Agent (AI for summaries)")
    print("9. Team monitored → Lead Agent (AI for pattern detection)")
    
    print("\nExecuting workflow...")
    invoice = orchestrator.process_invoice(invoice_file, source="workflow_demo")
    
    print("\nWorkflow completed!")
    print(f"Final status: {invoice.status.value}")
    print(f"Audit trail entries: {len(invoice.audit_trail)}")
    
    return orchestrator, invoice


def main():
    """Run all examples"""
    print("AI ACCOUNTS PAYABLE TEAM - EXAMPLES")
    print("="*60)
    print("\nThis script demonstrates the AI AP team functionality.")
    print("Each agent has a specific role and uses AI only where specified.\n")
    
    # Run examples
    try:
        # Example 1: Basic processing
        orchestrator1, invoice1 = example_1_basic_processing()
        
        # Example 2: Team monitoring
        # orchestrator2 = example_2_team_monitoring()
        
        # Example 3: Agent roles
        example_3_agent_roles()
        
        # Example 4: Complete workflow
        # orchestrator4, invoice4 = example_4_workflow()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
