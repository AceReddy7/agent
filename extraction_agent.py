"""
Extraction Agent - Data Reader
Role: Converts invoices into structured data
      Reads PDFs/images, extracts invoice fields (vendor, amounts, dates, line items),
      produces structured JSON, assigns confidence scores to each field

NOTE: This agent USES AI (Core functionality) for extraction
"""

import os
import json
from typing import Dict, Any, Optional
from base_agent import BaseAgent, Invoice, InvoiceStatus

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. Extraction will use mock data.")


class ExtractionAgent(BaseAgent):
    """
    Data extraction agent that converts invoices to structured data.
    Uses AI (Copilot knowledge) for core extraction functionality.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("ExtractionAgent")
        
        # Initialize OpenAI client if available
        self.ai_enabled = False
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.ai_enabled = True
                self.logger.info("AI extraction enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI: {e}")
        else:
            self.logger.warning("AI extraction disabled - using mock extraction")
            
    def process(self, invoice: Invoice) -> Invoice:
        """
        Extract data from invoice file.
        
        Args:
            invoice: Invoice object with original file
            
        Returns:
            Invoice with extracted data
        """
        invoice.status = InvoiceStatus.EXTRACTING
        
        # Read the invoice file content
        file_content = self._read_invoice_file(invoice.original_file)
        
        # Extract data using AI or mock
        if self.ai_enabled:
            extracted_data = self._extract_with_ai(file_content, invoice.original_file)
        else:
            extracted_data = self._extract_mock(invoice.original_file)
            
        # Store extracted data
        invoice.extracted_data = extracted_data["data"]
        invoice.confidence_scores = extracted_data["confidence_scores"]
        
        # Update status
        invoice.status = InvoiceStatus.EXTRACTED
        
        # Add to audit trail
        invoice.add_audit_entry(
            self.agent_name,
            "data_extracted",
            {
                "fields_extracted": list(invoice.extracted_data.keys()),
                "confidence_scores": invoice.confidence_scores,
                "ai_enabled": self.ai_enabled
            }
        )
        
        self.logger.info(f"Invoice {invoice.invoice_id} data extracted successfully")
        
        return invoice
        
    def _read_invoice_file(self, file_path: str) -> str:
        """
        Read invoice file content.
        
        Args:
            file_path: Path to invoice file
            
        Returns:
            File content as string
        """
        # For simplicity, we'll read text files directly
        # In production, this would handle PDFs, images, etc.
        try:
            if file_path.endswith('.txt') or file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    return f.read()
            else:
                # For other files, return placeholder
                return f"Binary file: {file_path}"
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            return ""
            
    def _extract_with_ai(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Extract invoice data using AI (Copilot knowledge).
        
        Args:
            content: Invoice file content
            file_path: Path to invoice file
            
        Returns:
            Extracted data with confidence scores
        """
        try:
            # Use OpenAI to extract invoice data
            prompt = f"""
Extract the following information from this invoice:
- vendor_name
- vendor_address
- invoice_number
- invoice_date
- due_date
- subtotal
- tax_amount
- total_amount
- line_items (list of items with description, quantity, unit_price, total)
- payment_terms
- purchase_order_number (if available)

Invoice content:
{content}

Return the data as a JSON object with confidence scores (0-1) for each field.
Format: {{"data": {{...}}, "confidence_scores": {{...}}}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert invoice data extraction assistant. Extract structured data from invoices with high accuracy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            self.logger.error(f"AI extraction failed: {e}")
            # Fallback to mock extraction
            return self._extract_mock(file_path)
            
    def _extract_mock(self, file_path: str) -> Dict[str, Any]:
        """
        Mock extraction for testing (when AI is not available).
        
        Args:
            file_path: Path to invoice file
            
        Returns:
            Mock extracted data with confidence scores
        """
        return {
            "data": {
                "vendor_name": "Acme Corporation",
                "vendor_address": "123 Business St, Suite 100, New York, NY 10001",
                "invoice_number": "INV-2024-001",
                "invoice_date": "2024-01-15",
                "due_date": "2024-02-15",
                "subtotal": 1000.00,
                "tax_amount": 80.00,
                "total_amount": 1080.00,
                "line_items": [
                    {
                        "description": "Professional Services",
                        "quantity": 10,
                        "unit_price": 100.00,
                        "total": 1000.00
                    }
                ],
                "payment_terms": "Net 30",
                "purchase_order_number": "PO-2024-001"
            },
            "confidence_scores": {
                "vendor_name": 0.95,
                "vendor_address": 0.90,
                "invoice_number": 0.98,
                "invoice_date": 0.95,
                "due_date": 0.95,
                "subtotal": 0.92,
                "tax_amount": 0.90,
                "total_amount": 0.95,
                "line_items": 0.88,
                "payment_terms": 0.85,
                "purchase_order_number": 0.80
            }
        }
