"""
Mock Azure Services Client voor demo doeleinden
In productie zou dit echte Azure SDK calls maken
"""

import time
import json
import requests
from typing import Dict, List, Any, Optional
import logging
try:
    from config import config
except Exception:
    class _Fallback:
        USE_MOCK_AZURE = True
        AZURE_FUNCTION_URL = None
        AZURE_STORAGE_ACCOUNT = None
    config = _Fallback()

class AzureServicesClient:
    """Mock client voor Azure services communicatie"""
    
    def __init__(self, function_app_url: Optional[str] = None, storage_account: Optional[str] = None):
        self.function_app_url = (
            function_app_url or config.AZURE_FUNCTION_URL or "https://your-function-app.azurewebsites.net"
        )
        self.storage_account = (
            storage_account or config.AZURE_STORAGE_ACCOUNT or "yourstorageaccount"
        )
        self.api_key = "mock_api_key"  # In productie uit Key Vault
        
    def convert_pdf_to_text(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Convert PDF naar tekst via Azure Function
        
        Args:
            file_content: PDF bestand als bytes
            filename: Naam van het bestand
            
        Returns:
            Dict met resultaat van conversie
        """
        try:
            # Mock implementatie - in productie zou dit een echte HTTP call zijn
            logging.info(f"Converting PDF to text: {filename}")
            
            # Simuleer API call delay
            time.sleep(1)
            
            # Mock response gebaseerd op filename
            if "sample" in filename.lower():
                mock_text = self._get_sample_pdf_text()
            else:
                mock_text = self._generate_mock_text(filename)
            
            return {
                "success": True,
                "text": mock_text,
                "blob_url": f"https://{self.storage_account}.blob.core.windows.net/documents/extracted_text/{filename}_{int(time.time())}.txt",
                "processing_time": time.time(),
                "confidence": 0.95
            }
            
        except Exception as e:
            logging.error(f"Error in PDF conversion: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_purchase_order_data(self, text: str) -> Dict[str, Any]:
        """
        Extraheer gestructureerde data uit tekst via Azure Function
        
        Args:
            text: Geconverteerde tekst uit PDF
            
        Returns:
            Dict met geëxtraheerde gestructureerde data
        """
        try:
            logging.info("Extracting structured data from text")
            
            # Simuleer API call delay
            time.sleep(2)
            
            # Mock extractie gebaseerd op tekst content
            extracted_data = self._extract_mock_data(text)
            
            return {
                "success": True,
                "extracted_data": extracted_data,
                "blob_url": f"https://{self.storage_account}.blob.core.windows.net/documents/extracted_data/order_{int(time.time())}.json",
                "confidence_score": self._calculate_mock_confidence(extracted_data)
            }
            
        except Exception as e:
            logging.error(f"Error in data extraction: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_processed_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sla verwerkt document op in Azure Blob Storage
        
        Args:
            document_data: Gevalideerde document data
            
        Returns:
            Dict met opslag resultaat
        """
        try:
            logging.info("Saving processed document to blob storage")
            
            # Simuleer opslag delay
            time.sleep(1)
            
            blob_name = f"processed_orders/{document_data.get('order_number', 'unknown')}_{int(time.time())}.json"
            
            return {
                "success": True,
                "blob_name": blob_name,
                "blob_url": f"https://{self.storage_account}.blob.core.windows.net/documents/{blob_name}",
                "size_bytes": len(json.dumps(document_data))
            }
            
        except Exception as e:
            logging.error(f"Error saving document: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """
        Krijg status van document verwerking
        
        Args:
            document_id: Unieke document identifier
            
        Returns:
            Dict met document status
        """
        try:
            # Mock status gebaseerd op document_id
            if document_id.startswith("APO"):
                status = "completed" if int(document_id[-1]) % 2 == 0 else "processing"
            else:
                status = "pending"
            
            return {
                "document_id": document_id,
                "status": status,
                "created_at": time.time() - 3600,  # 1 uur geleden
                "updated_at": time.time(),
                "processing_steps": {
                    "upload": "completed",
                    "convert": "completed" if status != "pending" else "pending",
                    "extract": "completed" if status == "completed" else "pending",
                    "validate": "completed" if status == "completed" else "pending"
                }
            }
            
        except Exception as e:
            logging.error(f"Error getting document status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_sample_pdf_text(self) -> str:
        """Geef sample PDF tekst terug voor demo"""
        return """
PURCHASE ORDER

Order Number: APO-00199
Date: 2024-01-15
Supplier: JASA Packaging Solutions B.V.
Contact: +31 20 1234567
Email: orders@jasa-packaging.nl

Ship To:
HSO Nederland B.V.
Postbus 12345
1234 AB Amsterdam
Netherlands

Bill To:
HSO Nederland B.V.
Accounting Department
Postbus 12345
1234 AB Amsterdam
Netherlands

Items:
- Premium Packaging Boxes (Large): 100 units @ €25.00 = €2,500.00
- Bubble Wrap Rolls (50m): 50 units @ €15.00 = €750.00
- Shipping Labels (1000 pcs): 5 units @ €12.50 = €62.50
- Tape Dispenser: 2 units @ €8.75 = €17.50

Subtotal: €3,330.00
Discount (5%): €166.50
Net Subtotal: €3,163.50
VAT (21%): €664.34
Total: €3,827.84

Payment Terms: Net 30 days
Delivery Date: 2024-01-30
Reference: PO-2024-001

Authorized by: Jane Doe
Title: Procurement Manager
Signature: [Signature]
Date: 2024-01-15
        """.strip()
    
    def _generate_mock_text(self, filename: str) -> str:
        """Genereer mock tekst gebaseerd op bestandsnaam"""
        order_num = filename.replace('.pdf', '').upper()
        
        return f"""
PURCHASE ORDER

Order Number: {order_num}
Date: 2024-01-15
Supplier: Mock Supplier B.V.

Items:
- Product A: 100 units @ €25.00 = €2,500.00
- Product B: 50 units @ €15.00 = €750.00

Subtotal: €3,250.00
VAT (21%): €682.50
Total: €3,932.50

Delivery Address:
HSO Nederland B.V.
Postbus 12345
1234 AB Amsterdam
        """.strip()
    
    def _extract_mock_data(self, text: str) -> Dict[str, Any]:
        """Extraheer mock data uit tekst"""
        
        # Eenvoudige extractie voor demo
        import re
        
        # Order number
        order_match = re.search(r'Order Number:\s*([A-Z0-9-]+)', text)
        order_number = order_match.group(1) if order_match else "APO-00199"
        
        # Date
        date_match = re.search(r'Date:\s*(\d{4}-\d{2}-\d{2})', text)
        date = date_match.group(1) if date_match else "2024-01-15"
        
        # Supplier
        supplier_match = re.search(r'Supplier:\s*([^\n]+)', text)
        supplier = supplier_match.group(1).strip() if supplier_match else "Mock Supplier B.V."
        
        # Items - verbeterde extractie
        items = []
        item_pattern = r'-\s*([^:]+):\s*(\d+)\s*units?\s*@\s*€(\d+\.?\d*)\s*=\s*€(\d+\.?\d*)'
        item_matches = re.findall(item_pattern, text)
        
        for match in item_matches:
            items.append({
                "product": match[0].strip(),
                "quantity": int(match[1]),
                "unit_price": float(match[2]),
                "total": float(match[3])
            })
        
        # Totals
        subtotal_match = re.search(r'Subtotal:\s*€(\d+\.?\d*)', text)
        subtotal = float(subtotal_match.group(1)) if subtotal_match else sum(item['total'] for item in items)
        
        vat_match = re.search(r'VAT\s*\((\d+)%\):\s*€(\d+\.?\d*)', text)
        vat_rate = float(vat_match.group(1)) / 100 if vat_match else 0.21
        vat_amount = float(vat_match.group(2)) if vat_match else subtotal * vat_rate
        
        total_match = re.search(r'Total:\s*€(\d+\.?\d*)', text)
        total = float(total_match.group(1)) if total_match else subtotal + vat_amount
        
        return {
            "order_number": order_number,
            "date": date,
            "supplier": supplier,
            "items": items,
            "subtotal": subtotal,
            "vat_rate": vat_rate,
            "vat_amount": vat_amount,
            "total": total,
            "delivery_address": {
                "company": "HSO Nederland B.V.",
                "address": "Postbus 12345, 1234 AB Amsterdam"
            },
            "metadata": {
                "extracted_at": time.time(),
                "source": "mock_extraction"
            }
        }
    
    def _calculate_mock_confidence(self, data: Dict[str, Any]) -> float:
        """Bereken mock confidence score"""
        score = 0.0
        
        if data.get('order_number'):
            score += 0.25
        if data.get('date'):
            score += 0.15
        if data.get('supplier'):
            score += 0.20
        if data.get('items') and len(data['items']) > 0:
            score += 0.25
        if data.get('total') and data.get('subtotal'):
            score += 0.15
            
        return round(score, 2)

# Factory function voor productie vs mock
def get_azure_client(use_mock: Optional[bool] = None) -> AzureServicesClient:
    """
    Factory function om Azure client te krijgen
    
    Args:
        use_mock: Of mock client gebruikt moet worden. Als None, gebruik configuratie.
        
    Returns:
        AzureServicesClient instance
    """
    # Als parameter niet gespecificeerd is, val terug op configuratie
    if use_mock is None:
        use_mock = getattr(config, "USE_MOCK_AZURE", True)

    if use_mock:
        return AzureServicesClient()
    else:
        # In productie zou dit echte Azure configuratie laden
        return AzureServicesClient(
            function_app_url=config.AZURE_FUNCTION_URL or "https://your-real-function-app.azurewebsites.net",
            storage_account=config.AZURE_STORAGE_ACCOUNT or "yourrealstorage"
        )
