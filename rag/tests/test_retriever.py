import unittest
from unittest.mock import patch, MagicMock

from rag.src.rag.utils.retriever import Retriever
from rag.src.rag.utils.milvus_manager import MilvusManager

class TestRetriever(unittest.TestCase):

    @patch('rag.src.rag.utils.retriever.boto3.client')
    @patch('rag.src.rag.utils.retriever.cohere.Client')
    def setUp(self, mock_cohere_client, mock_boto3_client):
        """Set up the test case with mocked dependencies."""
        self.mock_milvus_manager = MagicMock(spec=MilvusManager)
        self.mock_bedrock_client = MagicMock()
        self.mock_cohere_client = MagicMock()
        
        mock_boto3_client.return_value = self.mock_bedrock_client
        mock_cohere_client.return_value = self.mock_cohere_client

        self.retriever = Retriever(milvus_manager=self.mock_milvus_manager)

    def test_initialization(self):
        """Test that the Retriever initializes correctly."""
        self.assertIsNotNone(self.retriever)
        self.assertEqual(self.retriever.milvus_manager, self.mock_milvus_manager)
        self.assertTrue(self.retriever.bedrock_client)
        self.assertTrue(self.retriever.cohere_client)

    def test_retrieve_and_synthesize_flow(self):
        """Test the full retrieve_and_synthesize workflow."""
        # Arrange
        query = "What is the process for X?"
        dummy_embedding = [0.3] * 768
        dummy_search_results = [
            {"id": 1, "score": 0.9, "entity": {"text": "Document about X process step 1."}},
            {"id": 2, "score": 0.8, "entity": {"text": "Document about X process step 2."}},
        ]
        dummy_reranked_docs = [
            "Document about X process step 2.",
            "Document about X process step 1.",
        ]
        dummy_guide = "Step 1: Do the second thing. Step 2: Do the first thing."

        # Mock the internal methods
        self.retriever._embed_query = MagicMock(return_value=dummy_embedding)
        self.retriever._search_milvus = MagicMock(return_value=dummy_search_results)
        self.retriever._rerank_results = MagicMock(return_value=dummy_reranked_docs)
        self.retriever._synthesize_preliminary_guide = MagicMock(return_value=dummy_guide)

        # Act
        result = self.retriever.retrieve_and_synthesize(query)

        # Assert
        self.retriever._embed_query.assert_called_once_with(query)
        self.retriever._search_milvus.assert_called_once_with(dummy_embedding, top_n=50)
        self.retriever._rerank_results.assert_called_once_with(query, dummy_search_results)
        self.retriever._synthesize_preliminary_guide.assert_called_once_with(query, dummy_reranked_docs[:5])
        self.assertEqual(result, dummy_guide)

if __name__ == '__main__':
    unittest.main()
