"""
Unit tests voor Azure Services Client
Tests voor de mock en echte Azure service integraties
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
import time

# Add parent directory to path voor imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.azure_client import AzureServicesClient, get_azure_client

class TestAzureServicesClient(unittest.TestCase):
    """Test cases voor AzureServicesClient"""
    
    def setUp(self):
        """Setup voor elke test"""
        self.client = AzureServicesClient()
        self.sample_pdf_content = b"Mock PDF content"
        self.sample_text = """
        PURCHASE ORDER
        
        Order Number: APO-00199
        Date: 2024-01-15
        Supplier: JASA Packaging Solutions B.V.
        
        Items:
        - Product A: 100 units @ €25.00 = €2,500.00
        - Product B: 50 units @ €15.00 = €750.00
        
        Subtotal: €3,250.00
        VAT (21%): €682.50
        Total: €3,932.50
        """
    
    def test_convert_pdf_to_text_success(self):
        """Test successful PDF to text conversion"""
        result = self.client.convert_pdf_to_text(
            self.sample_pdf_content, 
            "test_sample.pdf"
        )
        
        self.assertTrue(result["success"])
        self.assertIn("text", result)
        self.assertIn("blob_url", result)
        self.assertIn("processing_time", result)
        self.assertIn("confidence", result)
        self.assertIsInstance(result["text"], str)
        self.assertGreater(len(result["text"]), 0)
    
    def test_convert_pdf_to_text_with_sample_filename(self):
        """Test dat sample bestanden de juiste mock data krijgen"""
        result = self.client.convert_pdf_to_text(
            self.sample_pdf_content, 
            "sample_document.pdf"
        )
        
        self.assertTrue(result["success"])
        self.assertIn("JASA Packaging Solutions", result["text"])
        self.assertIn("APO-00199", result["text"])
    
    def test_extract_purchase_order_data_success(self):
        """Test successful data extraction"""
        result = self.client.extract_purchase_order_data(self.sample_text)
        
        self.assertTrue(result["success"])
        self.assertIn("extracted_data", result)
        self.assertIn("confidence_score", result)
        
        data = result["extracted_data"]
        self.assertEqual(data["order_number"], "APO-00199")
        self.assertEqual(data["date"], "2024-01-15")
        self.assertEqual(data["supplier"], "JASA Packaging Solutions B.V.")
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["subtotal"], 3250.00)
        self.assertEqual(data["total"], 3932.50)
    
    def test_extract_purchase_order_data_items_parsing(self):
        """Test dat line items correct geparsed worden"""
        result = self.client.extract_purchase_order_data(self.sample_text)
        data = result["extracted_data"]
        
        self.assertEqual(len(data["items"]), 2)
        
        # Test eerste item
        item1 = data["items"][0]
        self.assertEqual(item1["product"], "Product A")
        self.assertEqual(item1["quantity"], 100)
        self.assertEqual(item1["unit_price"], 25.00)
        self.assertEqual(item1["total"], 2500.00)
        
        # Test tweede item
        item2 = data["items"][1]
        self.assertEqual(item2["product"], "Product B")
        self.assertEqual(item2["quantity"], 50)
        self.assertEqual(item2["unit_price"], 15.00)
        self.assertEqual(item2["total"], 750.00)
    
    def test_save_processed_document_success(self):
        """Test successful document saving"""
        test_data = {
            "order_number": "APO-00199",
            "supplier": "Test Supplier",
            "total": 1000.00
        }
        
        result = self.client.save_processed_document(test_data)
        
        self.assertTrue(result["success"])
        self.assertIn("blob_name", result)
        self.assertIn("blob_url", result)
        self.assertIn("size_bytes", result)
        self.assertIn("APO-00199", result["blob_name"])
    
    def test_get_document_status_completed(self):
        """Test document status voor completed documents"""
        # Even numbers should return completed status
        result = self.client.get_document_status("APO-00198")
        
        self.assertEqual(result["document_id"], "APO-00198")
        self.assertEqual(result["status"], "completed")
        self.assertIn("processing_steps", result)
        
        steps = result["processing_steps"]
        self.assertEqual(steps["upload"], "completed")
        self.assertEqual(steps["convert"], "completed")
        self.assertEqual(steps["extract"], "completed")
        self.assertEqual(steps["validate"], "completed")
    
    def test_get_document_status_processing(self):
        """Test document status voor processing documents"""
        # Odd numbers should return processing status
        result = self.client.get_document_status("APO-00199")
        
        self.assertEqual(result["document_id"], "APO-00199")
        self.assertEqual(result["status"], "processing")
    
    def test_calculate_mock_confidence_full_data(self):
        """Test confidence calculation met complete data"""
        complete_data = {
            "order_number": "APO-00199",
            "date": "2024-01-15",
            "supplier": "Test Supplier",
            "items": [{"product": "Test", "quantity": 1}],
            "total": 100.00,
            "subtotal": 85.00
        }
        
        confidence = self.client._calculate_mock_confidence(complete_data)
        self.assertEqual(confidence, 1.0)  # All fields present = 100%
    
    def test_calculate_mock_confidence_partial_data(self):
        """Test confidence calculation met incomplete data"""
        partial_data = {
            "order_number": "APO-00199",
            "supplier": "Test Supplier"
        }
        
        confidence = self.client._calculate_mock_confidence(partial_data)
        self.assertEqual(confidence, 0.45)  # 0.25 + 0.20 = 0.45
    
    def test_extract_mock_data_with_empty_text(self):
        """Test data extraction met lege tekst"""
        result = self.client._extract_mock_data("")
        
        # Should return default values
        self.assertEqual(result["order_number"], "APO-00199")
        self.assertEqual(result["date"], "2024-01-15")
        self.assertEqual(result["supplier"], "Mock Supplier B.V.")
        self.assertEqual(len(result["items"]), 0)
    
    def test_extract_mock_data_with_custom_order_number(self):
        """Test dat custom order numbers correct geëxtraheerd worden"""
        custom_text = "Order Number: CUSTOM-12345\nDate: 2024-02-01"
        result = self.client._extract_mock_data(custom_text)
        
        self.assertEqual(result["order_number"], "CUSTOM-12345")
        self.assertEqual(result["date"], "2024-02-01")

class TestAzureClientFactory(unittest.TestCase):
    """Test cases voor de factory function"""
    
    def test_get_azure_client_mock(self):
        """Test dat factory mock client teruggeeft"""
        client = get_azure_client(use_mock=True)
        self.assertIsInstance(client, AzureServicesClient)
        self.assertEqual(client.function_app_url, "https://your-function-app.azurewebsites.net")
    
    def test_get_azure_client_production(self):
        """Test dat factory production client teruggeeft"""
        client = get_azure_client(use_mock=False)
        self.assertIsInstance(client, AzureServicesClient)
        self.assertEqual(client.function_app_url, "https://your-real-function-app.azurewebsites.net")

class TestAzureClientErrorHandling(unittest.TestCase):
    """Test cases voor error handling scenarios"""
    
    def setUp(self):
        self.client = AzureServicesClient()
    
    @patch('services.azure_client.time.sleep')  # Mock sleep voor snellere tests
    def test_convert_pdf_with_exception(self, mock_sleep):
        """Test error handling bij PDF conversie"""
        # Force an exception in the conversion process
        with patch.object(self.client, '_get_sample_pdf_text', side_effect=Exception("Test error")):
            result = self.client.convert_pdf_to_text(b"test", "test.pdf")
            
            self.assertFalse(result["success"])
            self.assertIn("error", result)
            self.assertIn("Test error", result["error"])
    
    @patch('services.azure_client.time.sleep')
    def test_extract_data_with_exception(self, mock_sleep):
        """Test error handling bij data extractie"""
        with patch.object(self.client, '_extract_mock_data', side_effect=Exception("Extraction error")):
            result = self.client.extract_purchase_order_data("test text")
            
            self.assertFalse(result["success"])
            self.assertIn("error", result)
            self.assertIn("Extraction error", result["error"])
    
    @patch('services.azure_client.time.sleep')
    def test_save_document_with_exception(self, mock_sleep):
        """Test error handling bij document opslag"""
        with patch('services.azure_client.json.dumps', side_effect=Exception("JSON error")):
            result = self.client.save_processed_document({"test": "data"})
            
            self.assertFalse(result["success"])
            self.assertIn("error", result)

class TestDataExtractionRegex(unittest.TestCase):
    """Test cases voor regex patterns in data extractie"""
    
    def setUp(self):
        self.client = AzureServicesClient()
    
    def test_order_number_variations(self):
        """Test verschillende order number formaten"""
        test_cases = [
            ("Order Number: APO-12345", "APO-12345"),
            ("Purchase Order: PO-67890", "PO-67890"),
            ("PO: ABC123", "ABC123"),
            ("order number APO-999", "APO-999")
        ]
        
        for text, expected in test_cases:
            result = self.client._extract_mock_data(text)
            self.assertEqual(result["order_number"], expected, f"Failed for text: {text}")
    
    def test_date_format_variations(self):
        """Test verschillende datum formaten"""
        test_cases = [
            ("Date: 2024-01-15", "2024-01-15"),
            ("Date: 15/01/2024", "15/01/2024"),
            ("01-01-2024", "01-01-2024")
        ]
        
        for text, expected in test_cases:
            result = self.client._extract_mock_data(text)
            self.assertEqual(result["date"], expected, f"Failed for text: {text}")
    
    def test_item_parsing_variations(self):
        """Test verschillende item line formaten"""
        test_text = """
        - Product A: 100 units @ €25.00 = €2500.00
        * Product B: 50 units @ €15 = €750
        • Product C: 25 units @ €10.50 = €262.50
        """
        
        result = self.client._extract_mock_data(test_text)
        self.assertEqual(len(result["items"]), 3)
        
        # Test eerste item
        self.assertEqual(result["items"][0]["product"], "Product A")
        self.assertEqual(result["items"][0]["quantity"], 100)
        self.assertEqual(result["items"][0]["unit_price"], 25.00)

if __name__ == '__main__':
    # Run alle tests
    unittest.main(verbosity=2)
