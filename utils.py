"""
Utility functions for the AI Accounts Payable Team.

This module contains common utilities used across agents for error handling,
logging, and data processing.
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime


def format_currency(amount: float) -> str:
    """Format a number as currency.
    
    Args:
        amount: Amount in dollars
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format a value as percentage.
    
    Args:
        value: Value between 0 and 1
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.1f}%"


def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary.
    
    Args:
        data: Dictionary to get value from
        key: Key to retrieve
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default
    """
    try:
        return data.get(key, default)
    except (TypeError, AttributeError):
        return default


def is_valid_amount(amount: Any) -> bool:
    """Check if a value is a valid amount.
    
    Args:
        amount: Value to check
        
    Returns:
        True if valid amount, False otherwise
    """
    try:
        num_amount = float(amount)
        return num_amount >= 0
    except (TypeError, ValueError):
        return False


def get_agent_logger(agent_name: str) -> logging.Logger:
    """Get a logger for an agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(agent_name)
    logger.setLevel(logging.INFO)
    return logger


def create_error_response(agent: str, error: str, invoice_id: str = None) -> Dict:
    """Create a standardized error response.
    
    Args:
        agent: Agent that encountered the error
        error: Error message
        invoice_id: Optional invoice ID
        
    Returns:
        Error response dictionary
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "error": error,
        "invoice_id": invoice_id,
        "severity": "error"
    }


def create_success_response(agent: str, data: Dict, invoice_id: str = None) -> Dict:
    """Create a standardized success response.
    
    Args:
        agent: Agent that processed the data
        data: Response data
        invoice_id: Optional invoice ID
        
    Returns:
        Success response dictionary
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "data": data,
        "invoice_id": invoice_id,
        "severity": "success"
    }


def calculate_success_rate(successful: int, total: int) -> float:
    """Calculate success rate.
    
    Args:
        successful: Number of successful items
        total: Total number of items
        
    Returns:
        Success rate as percentage (0-100)
    """
    if total == 0:
        return 0.0
    return (successful / total) * 100


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries.
    
    Args:
        *dicts: Variable number of dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple[bool, List[str]]:
    """Validate that required fields exist in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields
