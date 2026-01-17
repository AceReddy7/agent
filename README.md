# AI Accounts Payable Team

A fully automated AI-powered accounts payable processing system with specialized agents for each step of the invoice lifecycle.

## Overview

This project implements a complete AI Accounts Payable team consisting of 9 specialized agents that work together to process invoices from receipt to posting in the ERP system. Each agent has a specific role and uses AI only where specified for optimal efficiency.

## Architecture

The system follows a pipeline architecture where each invoice flows through specialized agents:

```
Invoice → Intake → Extraction → Validation → Matching → Compliance → Approvals → Posting → Audit
                                                  ↑
                                            Lead Agent
                                        (Monitors All)
```

## Agents and Their Roles

### 1. **Lead Agent** (Operational Supervisor)
- **Role**: Manages all 8 workers, not individual invoices
- **Responsibilities**:
  - Monitors all workers for bottlenecks and failures
  - Detects performance issues
  - Re-routes workloads when needed
  - Escalates unresolved issues
  - Produces team-level reports
- **AI Usage**: ⚠️ **Pattern Detection Only** - Uses AI to identify patterns in team performance

### 2. **Intake Agent** (Entry Point Worker)
- **Role**: Entry point for all invoices
- **Responsibilities**:
  - Receives invoices (upload/API)
  - Assigns unique invoice ID
  - Records source & timestamp
  - Stores original invoice immutably
  - Hands off to Extraction Agent
- **AI Usage**: ❌ **None** - Pure workflow agent

### 3. **Extraction Agent** (Data Reader)
- **Role**: Converts invoices into structured data
- **Responsibilities**:
  - Reads PDFs/images
  - Extracts invoice fields (vendor, amounts, dates, line items)
  - Produces structured JSON
  - Assigns confidence scores to each field
- **AI Usage**: ✅ **Core Functionality** - Uses AI for all data extraction

### 4. **Validation Agent** (First Quality Gate / Sanity Checker)
- **Role**: First quality gate for invoice data
- **Responsibilities**:
  - Validates vendor against master data
  - Detects duplicates
  - Checks required fields
  - Flags inconsistencies
- **AI Usage**: ❌ **None** - Rules-based validation only

### 5. **Matching Agent** (Financial Consistency Checker / PO Matcher)
- **Role**: Matches invoices to purchase orders
- **Responsibilities**:
  - Matches invoice to PO/receipt
  - Checks quantity, price, totals
  - Applies tolerance rules
  - Determines "clean" or "exception"
- **AI Usage**: ⚠️ **Edge Cases Only** - Uses AI only for complex matching scenarios

### 6. **Compliance Agent** (Regulatory Safety Layer / Policy & Tax Enforcer)
- **Role**: Ensures regulatory compliance
- **Responsibilities**:
  - Validates tax calculations
  - Applies jurisdiction rules
  - Enforces company spend policies
  - Flags compliance risks
- **AI Usage**: ⚠️ **Interpretation Only** - Uses AI to interpret complex compliance issues

### 7. **Approvals Agent** (Approval Logic Executor / Decision Router)
- **Role**: Routes invoices for approval
- **Responsibilities**:
  - Decides auto-approval vs escalation
  - Routes to correct approver
  - Enforces SLA timers
  - Records approval decisions
- **AI Usage**: ⚠️ **Risk Scoring Only** - Uses AI to calculate risk scores

### 8. **Posting Agent** (System of Record Writer / ERP Operator)
- **Role**: Posts approved invoices to ERP
- **Responsibilities**:
  - Posts invoice into ERP
  - Applies correct GL coding
  - Confirms posting success
  - Handles retries safely
- **AI Usage**: ❌ **None** - Direct system integration

### 9. **Audit Agent** (Continuous Oversight / Observer)
- **Role**: Maintains comprehensive audit trail
- **Responsibilities**:
  - Builds full audit trail per invoice
  - Tracks errors & anomalies
  - Monitors SLA performance
  - Generates audit-ready reports
- **AI Usage**: ⚠️ **Summaries Only** - Uses AI to generate audit summaries

## Agent AI Usage Summary

| Agent | AI Usage | Purpose |
|-------|----------|---------|
| Lead Agent | ⚠️ Pattern Detection | Detect patterns in team performance |
| Intake | ❌ None | Workflow only |
| Extraction | ✅ Core | Data extraction from documents |
| Validation | ❌ None | Rules-based validation |
| Matching | ⚠️ Edge Cases | Complex PO matching scenarios |
| Compliance | ⚠️ Interpretation | Interpret compliance issues |
| Approvals | ⚠️ Risk Scoring | Calculate approval risk scores |
| Posting | ❌ None | System integration |
| Audit | ⚠️ Summaries | Generate audit summaries |

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AceReddy7/agent.git
cd agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up OpenAI API key for AI features:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Note: The system works without OpenAI API key, but AI features will be disabled and mock data will be used.

## Usage

### Basic Usage

```python
from ap_team_orchestrator import APTeamOrchestrator

# Initialize the team
orchestrator = APTeamOrchestrator()

# Process an invoice
invoice = orchestrator.process_invoice('path/to/invoice.pdf', source='upload')

# Get team report
print(orchestrator.get_team_report())
```

### Run Examples

```bash
python example_usage.py
```

This will demonstrate:
- Basic invoice processing
- Team monitoring and reporting
- Complete workflow
- Agent roles and responsibilities

### Process Multiple Invoices

```python
from ap_team_orchestrator import APTeamOrchestrator

orchestrator = APTeamOrchestrator()

# Process multiple invoices
invoice_files = ['invoice1.pdf', 'invoice2.pdf', 'invoice3.pdf']

for file in invoice_files:
    invoice = orchestrator.process_invoice(file, source='batch')
    print(f"Processed: {invoice.invoice_id} - Status: {invoice.status.value}")

# Get team report
print(orchestrator.get_team_report())
```

### Monitor Team Performance

```python
# Monitor team for bottlenecks and failures
monitoring_report = orchestrator.monitor_team()
print(monitoring_report)

# Get SLA metrics
sla_metrics = orchestrator.get_sla_metrics()
print(sla_metrics)
```

## Features

### ✅ Complete Invoice Lifecycle
- Automated intake and ID assignment
- AI-powered data extraction
- Multi-stage validation and matching
- Compliance checking
- Automated approval routing
- ERP integration
- Comprehensive audit trails

### ✅ Intelligent Agent Design
- Each agent has a specific, focused role
- AI used only where it adds value
- Efficient processing pipeline
- Error handling and retry logic

### ✅ Team Management
- Lead agent monitors all workers
- Automatic bottleneck detection
- Workload re-routing
- Issue escalation
- Team performance reports

### ✅ Audit & Compliance
- Complete audit trail per invoice
- SLA monitoring
- Compliance risk flagging
- Audit-ready reports

### ✅ Extensible Architecture
- Easy to add new agents
- Modular design
- Clear separation of concerns
- Simple integration points

## Project Structure

```
agent/
├── base_agent.py              # Base agent framework
├── intake_agent.py            # Invoice intake (NO AI)
├── extraction_agent.py        # Data extraction (CORE AI)
├── validation_agent.py        # Data validation (NO AI)
├── matching_agent.py          # PO matching (AI for edge cases)
├── compliance_agent.py        # Compliance checking (AI for interpretation)
├── approvals_agent.py         # Approval routing (AI for risk scoring)
├── posting_agent.py           # ERP posting (NO AI)
├── audit_agent.py             # Audit trails (AI for summaries)
├── lead_agent.py              # Team management (AI for pattern detection)
├── ap_team_orchestrator.py   # Main orchestrator
├── example_usage.py           # Usage examples
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Configuration

### Auto-Approval Threshold
```python
orchestrator = APTeamOrchestrator()
orchestrator.approvals_agent.auto_approve_limit = 10000  # $10,000
```

### Tolerance for Matching
```python
orchestrator.matching_agent.tolerance = 0.05  # 5%
```

### SLA Timer
```python
orchestrator.approvals_agent.sla_hours = 48  # 48 hours
```

### Master Vendor List
```python
orchestrator.validation_agent.master_vendors = {
    "Acme Corporation",
    "TechSupply Inc",
    # ... more vendors
}
```

## Testing

Run the example usage to test all functionality:

```bash
python example_usage.py
```

This will:
1. Create sample invoices
2. Process them through the complete pipeline
3. Generate team reports
4. Demonstrate all agent capabilities

## API Integration

The system can be integrated with external systems:

### REST API Example
```python
from fastapi import FastAPI, UploadFile
from ap_team_orchestrator import APTeamOrchestrator

app = FastAPI()
orchestrator = APTeamOrchestrator()

@app.post("/process-invoice")
async def process_invoice(file: UploadFile):
    # Save uploaded file
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Process invoice
    invoice = orchestrator.process_invoice(file_path, source="api")
    
    return invoice.to_dict()
```

## Error Handling

The system includes comprehensive error handling:
- Automatic retry logic for posting failures
- Error tracking in audit trail
- Lead agent escalation for critical issues
- Detailed error reporting

## Performance Metrics

Track performance with built-in metrics:
- Processing time per invoice
- Success/failure rates per agent
- SLA compliance
- Bottleneck identification

## Future Enhancements

Potential improvements:
- Machine learning for approval predictions
- Advanced anomaly detection
- Multi-currency support
- Integration with more ERP systems
- Real-time dashboard
- Email notification system

## License

This project is provided as-is for demonstration and educational purposes.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

This AI Accounts Payable Team system demonstrates best practices in:
- Agent-based architecture
- AI/ML integration
- Financial workflow automation
- Audit and compliance tracking

---

**Note**: This is a demonstration project. For production use, additional security, scalability, and integration features should be implemented.