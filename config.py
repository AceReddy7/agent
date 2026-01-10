"""
Configuration constants for the AI Accounts Payable Team.

This module centralizes all configuration values, thresholds, and constants
used throughout the AP team agents.
"""

# Agent names
AGENT_INTAKE = "IntakeAgent"
AGENT_EXTRACTION = "ExtractionAgent"
AGENT_VALIDATION = "ValidationAgent"
AGENT_MATCHING = "MatchingAgent"
AGENT_COMPLIANCE = "ComplianceAgent"
AGENT_APPROVALS = "ApprovalsAgent"
AGENT_POSTING = "PostingAgent"
AGENT_AUDIT = "AuditAgent"
AGENT_LEAD = "LeadAgent"

ALL_AGENTS = [
    AGENT_INTAKE,
    AGENT_EXTRACTION,
    AGENT_VALIDATION,
    AGENT_MATCHING,
    AGENT_COMPLIANCE,
    AGENT_APPROVALS,
    AGENT_POSTING,
    AGENT_AUDIT
]

# Processing thresholds
AUTO_APPROVE_LIMIT = 5000.0  # Auto-approve invoices under this amount
FAILURE_THRESHOLD = 0.20  # 20% failure rate triggers alert
BOTTLENECK_THRESHOLD = 10  # 10 seconds processing time
SLA_HOURS = 48  # 48-hour approval SLA

# Risk scoring thresholds
HIGH_AMOUNT_THRESHOLD = 50000.0  # High-risk amount
MEDIUM_AMOUNT_THRESHOLD = 10000.0  # Medium-risk amount
LOW_AMOUNT_THRESHOLD = 5000.0  # Low-risk amount

HIGH_RISK_POINTS = 0.3  # Risk points for high amounts
MEDIUM_RISK_POINTS = 0.2  # Risk points for medium amounts
LOW_RISK_POINTS = 0.1  # Risk points for low amounts

# Confidence score thresholds
HIGH_CONFIDENCE = 0.95
MEDIUM_CONFIDENCE = 0.80
LOW_CONFIDENCE = 0.60

# File storage
DEFAULT_INVOICE_STORAGE = "./invoices"
DEFAULT_AUDIT_STORAGE = "./audit_trails"
DEFAULT_SAMPLE_STORAGE = "./sample_invoices"

# Default vendors (for validation)
DEFAULT_VENDORS = [
    "Acme Corporation",
    "Tech Solutions Inc",
    "Global Services Ltd",
    "Local Vendor LLC",
    "Premium Suppliers Co"
]

# Processing statuses
STATUS_PROCESSING = "processing"
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_EXCEPTION = "exception"
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"

# Approval routes
APPROVAL_ROUTE_AUTO = "auto"
APPROVAL_ROUTE_MANAGER = "manager"
APPROVAL_ROUTE_DIRECTOR = "director"
APPROVAL_ROUTE_CFO = "cfo"

# AI Model
AI_MODEL = "gpt-4"
AI_TEMPERATURE = 0.1  # Low temperature for consistent extraction
AI_PATTERN_TEMPERATURE = 0.3  # Slightly higher for pattern analysis

# Confidence scores (mock extraction defaults)
MOCK_CONFIDENCE_VENDOR_NAME = 0.95
MOCK_CONFIDENCE_VENDOR_ADDRESS = 0.90
MOCK_CONFIDENCE_INVOICE_NUMBER = 0.98
MOCK_CONFIDENCE_INVOICE_DATE = 0.95
MOCK_CONFIDENCE_DUE_DATE = 0.95
MOCK_CONFIDENCE_SUBTOTAL = 0.92
MOCK_CONFIDENCE_TAX_AMOUNT = 0.90
MOCK_CONFIDENCE_TOTAL_AMOUNT = 0.95
MOCK_CONFIDENCE_LINE_ITEMS = 0.88
MOCK_CONFIDENCE_PAYMENT_TERMS = 0.85
MOCK_CONFIDENCE_PO_NUMBER = 0.80

# Logging
LOG_FORMAT = '%(levelname)s:%(name)s:%(message)s'
LOG_LEVEL = 'INFO'

# Report settings
REPORT_ESCALATIONS_LIMIT = 5  # Show last N escalations in report
