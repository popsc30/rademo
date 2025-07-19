import unittest
from unittest.mock import patch, MagicMock

from rag.src.rag.utils.milvus_manager import MilvusManager

@patch('rag.src.rag.utils.milvus_manager.connections')
@patch('rag.src.rag.utils.milvus_manager.utility')
@patch('rag.src.rag.utils.milvus_manager.Collection')
@patch('rag.src.rag.utils.milvus_manager.CollectionSchema')
@patch('rag.src.rag.utils.milvus_manager.FieldSchema')
class TestMilvusManager(unittest.TestCase):

    def test_initialization_collection_exists(self, mock_field_schema, mock_collection_schema, mock_collection_class, mock_utility, mock_connections):
        """Test initialization when the collection already exists."""
        mock_utility.has_collection.return_value = True
        mock_collection_instance = MagicMock()
        mock_collection_class.return_value = mock_collection_instance

        manager = MilvusManager()

        mock_connections.connect.assert_called_once_with("default", host="127.0.0.1", port="19530")
        mock_utility.has_collection.assert_called_once_with("rag_collection")
        mock_collection_class.assert_called_once_with("rag_collection")
        self.assertEqual(manager.collection, mock_collection_instance)
        mock_collection_instance.create_index.assert_not_called()

    def test_initialization_collection_does_not_exist(self, mock_field_schema, mock_collection_schema, mock_collection_class, mock_utility, mock_connections):
        """Test initialization when the collection needs to be created."""
        mock_utility.has_collection.return_value = False
        mock_collection_instance = MagicMock()
        mock_collection_class.return_value = mock_collection_instance

        manager = MilvusManager()

        mock_connections.connect.assert_called_once_with("default", host="127.0.0.1", port="19530")
        mock_utility.has_collection.assert_called_once_with("rag_collection")
        self.assertTrue(mock_field_schema.called)
        self.assertTrue(mock_collection_schema.called)
        mock_collection_class.assert_called_with(name="rag_collection", schema=mock_collection_schema.return_value)
        mock_collection_instance.create_index.assert_called_once()

    def test_insert_data(self, mock_field_schema, mock_collection_schema, mock_collection_class, mock_utility, mock_connections):
        """Test the data insertion method."""
        mock_utility.has_collection.return_value = True
        mock_collection_instance = MagicMock()
        mock_collection_class.return_value = mock_collection_instance
        
        manager = MilvusManager()

        dummy_chunks = [
            {"embedding": [0.1] * 1536, "text": "chunk 1", "metadata": {"s": 1}},
            {"embedding": [0.2] * 1536, "text": "chunk 2", "metadata": {"s": 2}},
        ]
        
        mock_insert_result = MagicMock()
        mock_insert_result.primary_keys = [1, 2]
        mock_collection_instance.insert.return_value = mock_insert_result

        result = manager.insert_data(dummy_chunks)

        mock_collection_instance.insert.assert_called_once()
        mock_collection_instance.flush.assert_called_once()
        self.assertEqual(len(result.primary_keys), 2)

    def test_insert_no_data(self, mock_field_schema, mock_collection_schema, mock_collection_class, mock_utility, mock_connections):
        """Test that insert is not called when there is no data."""
        mock_utility.has_collection.return_value = True
        mock_collection_instance = MagicMock()
        mock_collection_class.return_value = mock_collection_instance
        
        manager = MilvusManager()
        
        manager.insert_data([])
        
        mock_collection_instance.insert.assert_not_called()

    def test_disconnect(self, mock_field_schema, mock_collection_schema, mock_collection_class, mock_utility, mock_connections):
        """Test the disconnect method."""
        mock_utility.has_collection.return_value = True
        
        manager = MilvusManager()
        manager.disconnect()
        
        mock_connections.disconnect.assert_called_once_with("default")

if __name__ == '__main__':
    unittest.main()
