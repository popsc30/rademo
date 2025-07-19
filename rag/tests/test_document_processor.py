import unittest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from rag.src.rag.utils.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):

    def setUp(self):
        """Set up a dummy file for testing."""
        self.test_file = "test_document.txt"
        with open(self.test_file, "w") as f:
            f.write("This is a simple test document.")
        
        # Mock the bedrock client to avoid actual API calls
        self.patcher = patch('rag.src.rag.utils.document_processor.boto3.client')
        self.mock_boto3_client = self.patcher.start()
        self.mock_bedrock_runtime = MagicMock()
        self.mock_boto3_client.return_value = self.mock_bedrock_runtime

    def tearDown(self):
        """Clean up the dummy file and stop the patcher."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.patcher.stop()

    def test_process_document_unsupported_file(self):
        """Test that an unsupported file type raises a ValueError."""
        processor = DocumentProcessor()
        with self.assertRaises(ValueError):
            processor.process_document(self.test_file)

    @patch('rag.src.rag.utils.document_processor.PdfReader')
    def test_process_pdf(self, mock_pdf_reader):
        """Test basic PDF processing workflow."""
        # Arrange
        mock_pdf_page = MagicMock()
        mock_pdf_page.extract_text.return_value = "This is PDF text."
        mock_pdf_reader.return_value.pages = [mock_pdf_page]
        
        processor = DocumentProcessor()
        
        # Mock the embedding call
        dummy_embedding = [0.1] * 768
        processor._generate_embeddings = MagicMock(return_value=[{"text": "This is PDF text.", "embedding": dummy_embedding, "metadata": {}}])

        # Act
        pdf_file = "dummy.pdf"
        result = processor.process_document(pdf_file)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['text'], "This is PDF text.")
        self.assertIn('embedding', result[0])
        processor._generate_embeddings.assert_called_once()

    @patch('rag.src.rag.utils.document_processor.docx.Document')
    def test_process_docx(self, mock_docx_document):
        """Test basic DOCX processing workflow."""
        # Arrange
        mock_para = MagicMock()
        mock_para.text = "This is DOCX text."
        mock_docx_document.return_value.paragraphs = [mock_para]

        processor = DocumentProcessor()

        # Mock the embedding call
        dummy_embedding = [0.2] * 768
        processor._generate_embeddings = MagicMock(return_value=[{"text": "This is DOCX text.", "embedding": dummy_embedding, "metadata": {}}])

        # Act
        docx_file = "dummy.docx"
        result = processor.process_document(docx_file)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['text'], "This is DOCX text.")
        self.assertIn('embedding', result[0])
        processor._generate_embeddings.assert_called_once()


if __name__ == '__main__':
    unittest.main()
