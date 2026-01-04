# Quick Start Guide - AI Accounts Payable Team

## Installation (2 minutes)

```bash
# Clone repository
git clone https://github.com/AceReddy7/agent.git
cd agent

# Install dependencies
pip install -r requirements.txt

# (Optional) Set OpenAI API key for AI features
export OPENAI_API_KEY="sk-..."
```

## Quick Test (30 seconds)

```bash
# Run the example
python example_usage.py
```

## Basic Usage

### Process a Single Invoice

```python
from ap_team_orchestrator import APTeamOrchestrator

# Initialize the team
orchestrator = APTeamOrchestrator()

# Process invoice
invoice = orchestrator.process_invoice('invoice.pdf', source='upload')

# Check status
print(f"Status: {invoice.status.value}")
print(f"Posted: {invoice.posting_results.get('posted')}")
```

### Process Multiple Invoices

```python
from ap_team_orchestrator import APTeamOrchestrator

orchestrator = APTeamOrchestrator()

invoices = ['inv1.pdf', 'inv2.pdf', 'inv3.pdf']
for inv_file in invoices:
    invoice = orchestrator.process_invoice(inv_file)
    print(f"✓ {invoice.invoice_id}: {invoice.status.value}")
```

### Get Team Report

```python
# Get comprehensive team report
report = orchestrator.get_team_report()
print(report)

# Get SLA metrics
metrics = orchestrator.get_sla_metrics()
print(f"SLA Compliance: {metrics['within_sla']}/{metrics['total_invoices']}")
```

## Agent Checklist

Each agent performs its designated role with AI only where specified:

✅ **Intake Agent** - NO AI  
&nbsp;&nbsp;&nbsp;&nbsp;Receives invoices, assigns IDs, stores immutably

✅ **Extraction Agent** - CORE AI  
&nbsp;&nbsp;&nbsp;&nbsp;Extracts all data from documents

✅ **Validation Agent** - NO AI  
&nbsp;&nbsp;&nbsp;&nbsp;Validates data, checks duplicates, verifies consistency

✅ **Matching Agent** - EDGE CASES ONLY  
&nbsp;&nbsp;&nbsp;&nbsp;Matches to POs, applies tolerance rules

✅ **Compliance Agent** - INTERPRETATION ONLY  
&nbsp;&nbsp;&nbsp;&nbsp;Checks tax, jurisdiction, policies

✅ **Approvals Agent** - RISK SCORING ONLY  
&nbsp;&nbsp;&nbsp;&nbsp;Routes approvals based on risk

✅ **Posting Agent** - NO AI  
&nbsp;&nbsp;&nbsp;&nbsp;Posts to ERP with GL coding

✅ **Audit Agent** - SUMMARIES ONLY  
&nbsp;&nbsp;&nbsp;&nbsp;Creates audit trails and reports

✅ **Lead Agent** - PATTERN DETECTION ONLY  
&nbsp;&nbsp;&nbsp;&nbsp;Monitors team, detects bottlenecks

## Common Operations

### Check Invoice Status

```python
invoice = orchestrator.process_invoice('invoice.pdf')

# Status checks
print(f"Extracted: {bool(invoice.extracted_data)}")
print(f"Validated: {invoice.validation_results.get('passed')}")
print(f"Matched: {invoice.matching_results.get('is_clean')}")
print(f"Compliant: {invoice.compliance_results.get('compliant')}")
print(f"Approved: {invoice.approval_results.get('approval_decision')}")
print(f"Posted: {invoice.posting_results.get('posted')}")
```

### Review Errors

```python
invoice = orchestrator.process_invoice('invoice.pdf')

if invoice.errors:
    print("Errors found:")
    for error in invoice.errors:
        print(f"  [{error['agent']}] {error['error']}")
```

### Monitor Team

```python
# Monitor team performance
monitor_report = orchestrator.monitor_team()

print("Agent Performance:")
for agent in monitor_report['agents']:
    print(f"  {agent['agent']}: {agent['metrics']['successful']}/{agent['metrics']['processed']}")
```

## Configuration

### Auto-Approval Limit

```python
orchestrator = APTeamOrchestrator()
orchestrator.approvals_agent.auto_approve_limit = 10000  # $10,000
```

### Matching Tolerance

```python
orchestrator.matching_agent.tolerance = 0.05  # 5%
```

### Master Vendors

```python
orchestrator.validation_agent.master_vendors = {
    "Vendor A",
    "Vendor B",
    "Vendor C"
}
```

### GL Account Mapping

```python
orchestrator.posting_agent.gl_accounts = {
    "service": "5000",
    "supplies": "5100",
    "equipment": "1500"
}
```

## Troubleshooting

### AI Features Not Working

```bash
# Check if OpenAI key is set
echo $OPENAI_API_KEY

# Set the key
export OPENAI_API_KEY="sk-..."

# System works without AI key using mock data
```

### Invoice Validation Failing

```python
# Check validation results
print(invoice.validation_results)

# Common issues:
# - Vendor not in master list
# - Duplicate invoice number
# - Missing required fields
# - Math doesn't add up
```

### Matching Exceptions

```python
# Check matching results
print(invoice.matching_results)

# Common issues:
# - PO number not found
# - Quantity mismatch
# - Price exceeds tolerance
# - Total amount mismatch
```

### Posting Failures

```python
# Check posting results
print(invoice.posting_results)

# Check retry attempts
print(f"Attempts: {invoice.posting_results.get('attempts')}")
print(f"Errors: {invoice.posting_results.get('errors')}")
```

## File Locations

- **Original Invoices**: `./invoices/`
- **Audit Trails**: `./audit_trails/`
- **Sample Invoices**: `./sample_invoices/`

## Invoice Object Structure

```python
invoice.invoice_id              # Unique ID
invoice.status                  # Current status
invoice.extracted_data          # Extracted fields
invoice.validation_results      # Validation outcome
invoice.matching_results        # PO matching outcome
invoice.compliance_results      # Compliance check outcome
invoice.approval_results        # Approval decision
invoice.posting_results         # ERP posting outcome
invoice.audit_trail            # Complete history
invoice.errors                 # All errors
invoice.warnings               # All warnings
```

## Status Values

- `received` - Initial intake
- `extracting` - Data extraction in progress
- `extracted` - Data extracted
- `validating` - Validation in progress
- `validated` - Validation passed
- `matching` - PO matching in progress
- `matched` - PO matched
- `compliance_check` - Compliance check in progress
- `compliant` - Compliance passed
- `approval_pending` - Awaiting approval
- `approved` - Approved for posting
- `rejected` - Approval rejected
- `posting` - Posting to ERP
- `posted` - Successfully posted
- `failed` - Processing failed
- `exception` - Requires manual review

## Next Steps

1. Read [README.md](README.md) for comprehensive documentation
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
3. Run [example_usage.py](example_usage.py) to see all features
4. Customize agents for your specific needs
5. Integrate with your ERP system

## Support

- **Documentation**: See README.md and ARCHITECTURE.md
- **Examples**: Run example_usage.py
- **Issues**: Open GitHub issue

---

**Remember**: Each agent has a specific role and uses AI only where it adds value!
