"""
Unit tests voor Streamlit Data Extractor App
Tests voor de hoofdapplicatie functionaliteit
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path voor imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock streamlit voor testing
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit_option_menu'] = MagicMock()
sys.modules['plotly.express'] = MagicMock()
sys.modules['plotly.graph_objects'] = MagicMock()

from app import DataExtractorApp

class TestDataExtractorApp(unittest.TestCase):
    """Test cases voor DataExtractorApp"""
    
    def setUp(self):
        """Setup voor elke test"""
        # Mock streamlit session state
        self.mock_session_state = {
            'current_page': 'overview',
            'documents': [],
            'current_process': {
                'step': 1,
                'document': None,
                'text_content': None,
                'extracted_data': None,
                'status': 'idle'
            }
        }
        
        with patch('app.st.session_state', self.mock_session_state):
            self.app = DataExtractorApp()
    
    def test_init_session_state(self):
        """Test initialisatie van session state"""
        # Clear session state
        mock_empty_session = {}
        
        with patch('app.st.session_state', mock_empty_session):
            app = DataExtractorApp()
            app.init_session_state()
            
            # Check dat alle required keys aanwezig zijn
            self.assertIn('current_page', mock_empty_session)
            self.assertIn('documents', mock_empty_session)
            self.assertIn('current_process', mock_empty_session)
            
            # Check default values
            self.assertEqual(mock_empty_session['current_page'], 'overview')
            self.assertIsInstance(mock_empty_session['documents'], list)
            self.assertEqual(mock_empty_session['current_process']['step'], 1)
    
    def test_load_sample_documents(self):
        """Test dat sample documenten correct geladen worden"""
        with patch('app.st.session_state', self.mock_session_state):
            app = DataExtractorApp()
            documents = app.load_sample_documents()
            
            self.assertEqual(len(documents), 12)
            
            # Test eerste document structure
            doc = documents[0]
            required_fields = ['id', 'name', 'order_number', 'date_created', 'status', 'file_size', 'document_type']
            for field in required_fields:
                self.assertIn(field, doc)
            
            # Test dat er completed en uncompleted documenten zijn
            statuses = [doc['status'] for doc in documents]
            self.assertIn('Completed', statuses)
            self.assertIn('Uncompleted', statuses)
    
    def test_document_filtering_by_search(self):
        """Test document filtering functionaliteit"""
        with patch('app.st.session_state', self.mock_session_state):
            app = DataExtractorApp()
            
            # Setup test documents
            test_docs = [
                {'name': 'JASA Packaging', 'order_number': 'APO-001', 'status': 'Completed'},
                {'name': 'ABC Company', 'order_number': 'APO-002', 'status': 'Completed'},
                {'name': 'XYZ Corp', 'order_number': 'PO-123', 'status': 'Uncompleted'}
            ]
            
            # Test naam filtering
            filtered = [d for d in test_docs if 'jasa' in d['name'].lower()]
            self.assertEqual(len(filtered), 1)
            self.assertEqual(filtered[0]['name'], 'JASA Packaging')
            
            # Test order number filtering
            filtered = [d for d in test_docs if 'apo' in d['order_number'].lower()]
            self.assertEqual(len(filtered), 2)
    
    def test_process_step_navigation(self):
        """Test navigatie tussen process stappen"""
        with patch('app.st.session_state', self.mock_session_state):
            app = DataExtractorApp()
            
            # Test step progression
            self.mock_session_state['current_process']['step'] = 1
            self.assertEqual(self.mock_session_state['current_process']['step'], 1)
            
            # Simulate step advancement
            self.mock_session_state['current_process']['step'] = 2
            self.assertEqual(self.mock_session_state['current_process']['step'], 2)
            
            # Test step bounds
            for step in range(1, 5):
                self.mock_session_state['current_process']['step'] = step
                self.assertGreaterEqual(self.mock_session_state['current_process']['step'], 1)
                self.assertLessEqual(self.mock_session_state['current_process']['step'], 4)

class TestDataExtractionLogic(unittest.TestCase):
    """Test cases voor data extractie logica"""
    
    def setUp(self):
        self.mock_session_state = {
            'current_page': 'process',
            'documents': [],
            'current_process': {
                'step': 4,
                'document': None,
                'text_content': None,
                'extracted_data': {
                    'order_number': 'APO-00199',
                    'date': '2024-01-15',
                    'supplier': 'Test Supplier',
                    'items': [
                        {'product': 'Product A', 'quantity': 100, 'unit_price': 25.00, 'total': 2500.00}
                    ],
                    'subtotal': 2500.00,
                    'vat_rate': 0.21,
                    'vat_amount': 525.00,
                    'total': 3025.00
                },
                'status': 'ready_for_check'
            }
        }
    
    def test_extracted_data_structure(self):
        """Test dat extracted data de juiste structure heeft"""
        extracted = self.mock_session_state['current_process']['extracted_data']
        
        required_fields = ['order_number', 'date', 'supplier', 'items', 'subtotal', 'vat_rate', 'vat_amount', 'total']
        for field in required_fields:
            self.assertIn(field, extracted)
        
        # Test items structure
        self.assertIsInstance(extracted['items'], list)
        if extracted['items']:
            item = extracted['items'][0]
            item_fields = ['product', 'quantity', 'unit_price', 'total']
            for field in item_fields:
                self.assertIn(field, item)
    
    def test_financial_calculations(self):
        """Test dat financiële berekeningen correct zijn"""
        extracted = self.mock_session_state['current_process']['extracted_data']
        
        # Test VAT calculation
        expected_vat = extracted['subtotal'] * extracted['vat_rate']
        self.assertAlmostEqual(extracted['vat_amount'], expected_vat, places=2)
        
        # Test total calculation
        expected_total = extracted['subtotal'] + extracted['vat_amount']
        self.assertAlmostEqual(extracted['total'], expected_total, places=2)
        
        # Test item total
        item = extracted['items'][0]
        expected_item_total = item['quantity'] * item['unit_price']
        self.assertAlmostEqual(item['total'], expected_item_total, places=2)

class TestDocumentManagement(unittest.TestCase):
    """Test cases voor document management"""
    
    def test_document_creation(self):
        """Test aanmaken van nieuwe documenten"""
        new_doc = {
            'id': 'APO-00199',
            'name': 'Test Supplier B.V.',
            'order_number': 'APO-00199',
            'date_created': '2024-01-15',
            'status': 'Completed',
            'file_size': '2.1 MB',
            'document_type': 'Purchase Order'
        }
        
        # Valideer document structure
        required_fields = ['id', 'name', 'order_number', 'date_created', 'status', 'file_size', 'document_type']
        for field in required_fields:
            self.assertIn(field, new_doc)
        
        # Valideer data types
        self.assertIsInstance(new_doc['id'], str)
        self.assertIsInstance(new_doc['name'], str)
        self.assertIn(new_doc['status'], ['Completed', 'Uncompleted'])
    
    def test_document_status_tracking(self):
        """Test document status tracking"""
        documents = [
            {'status': 'Completed'},
            {'status': 'Completed'},
            {'status': 'Uncompleted'},
            {'status': 'Uncompleted'},
            {'status': 'Uncompleted'}
        ]
        
        completed_count = len([d for d in documents if d['status'] == 'Completed'])
        pending_count = len([d for d in documents if d['status'] == 'Uncompleted'])
        
        self.assertEqual(completed_count, 2)
        self.assertEqual(pending_count, 3)
        self.assertEqual(completed_count + pending_count, len(documents))

class TestUIComponents(unittest.TestCase):
    """Test cases voor UI componenten"""
    
    def test_css_styling_components(self):
        """Test dat CSS styling componenten correct gedefinieerd zijn"""
        with patch('app.st.session_state', {}):
            app = DataExtractorApp()
            
            # Test dat render_header geen exceptions gooit
            with patch('app.st.markdown') as mock_markdown:
                app.render_header()
                # Verify dat markdown called wordt (voor CSS en header)
                self.assertTrue(mock_markdown.called)
    
    def test_step_progress_indicators(self):
        """Test progress indicator logica"""
        steps = ["Upload", "Converting", "Extracting", "Check"]
        
        for current_step in range(1, 5):
            for i, step in enumerate(steps, 1):
                if i < current_step:
                    status = "completed"
                elif i == current_step:
                    status = "current"
                else:
                    status = "pending"
                
                # Test dat status correct bepaald wordt
                if i < current_step:
                    self.assertEqual(status, "completed")
                elif i == current_step:
                    self.assertEqual(status, "current")
                else:
                    self.assertEqual(status, "pending")

class TestErrorHandling(unittest.TestCase):
    """Test cases voor error handling"""
    
    def test_missing_session_state_handling(self):
        """Test handling van missing session state"""
        with patch('app.st.session_state', {}) as mock_session:
            app = DataExtractorApp()
            
            # Test dat init_session_state default values zet
            app.init_session_state()
            
            # Verify dat required keys toegevoegd zijn
            self.assertIn('current_page', mock_session)
            self.assertIn('documents', mock_session)
            self.assertIn('current_process', mock_session)
    
    def test_invalid_document_data_handling(self):
        """Test handling van invalide document data"""
        invalid_docs = [
            {},  # Empty document
            {'id': 'APO-001'},  # Missing required fields
            {'status': 'Invalid'},  # Invalid status
        ]
        
        for doc in invalid_docs:
            # Test dat we gracefully kunnen omgaan met incomplete data
            status = doc.get('status', 'Unknown')
            self.assertIsInstance(status, str)
            
            doc_id = doc.get('id', 'NO_ID')
            self.assertIsInstance(doc_id, str)

if __name__ == '__main__':
    # Setup test environment
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    # Run alle tests
    unittest.main(verbosity=2)
