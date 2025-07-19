from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
from loguru import logger

class MilvusManager:
    """
    Manages interactions with a Milvus Lite vector database.
    """

    def __init__(self, host: str = "127.0.0.1", port: str = "19530", collection_name: str = "rag_collection"):
        """
        Initializes the MilvusManager and connects to the Milvus server.
        Assumes that a Milvus instance (like Milvus Lite) is already running.
        """
        self.collection_name = collection_name
        try:
            connections.connect("default", host=host, port=port)
            logger.info("Successfully connected to Milvus.")
            self._create_collection_if_not_exists()
        except Exception as e:
            logger.exception(f"Error connecting to Milvus. Please ensure Milvus is running. Details: {e}")
            raise

    def _create_collection_if_not_exists(self):
        """
        Creates the collection in Milvus if it doesn't already exist.
        """
        if utility.has_collection(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' already exists.")
            self.collection = Collection(self.collection_name)
            self.collection.load()
            return

        logger.info(f"Collection '{self.collection_name}' not found. Creating new collection...")
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, description="Collection for RAG documents")
        self.collection = Collection(name=self.collection_name, schema=schema)

        # Create an index for the embedding field for efficient searching
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        self.collection.load()
        logger.info(f"Successfully created collection '{self.collection_name}', index, and loaded into memory.")

    def insert_data(self, processed_chunks: list):
        """
        Inserts processed data chunks into the Milvus collection.
        """
        if not processed_chunks:
            logger.warning("No data to insert.")
            return

        entities = [
            [chunk['embedding'] for chunk in processed_chunks],
            [chunk['text'] for chunk in processed_chunks],
            [chunk.get('metadata', {}) for chunk in processed_chunks]
        ]

        try:
            insert_result = self.collection.insert(entities)
            self.collection.flush()
            logger.info(f"Successfully inserted {len(insert_result.primary_keys)} entities.")
            return insert_result
        except Exception as e:
            logger.exception(f"Error inserting data into Milvus: {e}")
            return None

    def reset_collection(self):
        """
        Drops the collection if it exists.
        """
        if utility.has_collection(self.collection_name):
            logger.info(f"Dropping collection '{self.collection_name}'...")
            utility.drop_collection(self.collection_name)
            logger.info("Collection dropped.")
        else:
            logger.warning(f"Collection '{self.collection_name}' does not exist. Nothing to drop.")

    def disconnect(self):
        """
        Disconnects from the Milvus server.
        """
        connections.disconnect("default")
        logger.info("Disconnected from Milvus.")

if __name__ == '__main__':
    logger.info("Running Milvus manager example...")
    try:
        # This example requires a running Milvus instance.
        milvus_manager = MilvusManager()
        dummy_chunks = [
            {"embedding": [0.1] * 768, "text": "Test chunk 1.", "metadata": {"source": "test.txt"}},
            {"embedding": [0.2] * 768, "text": "Test chunk 2.", "metadata": {"source": "test.txt"}}
        ]
        milvus_manager.insert_data(dummy_chunks)
        milvus_manager.disconnect()
        logger.info("Milvus manager example finished.")
    except Exception as e:
        logger.exception(f"An error occurred during the example: {e}")
        logger.error("Please ensure you have a Milvus instance running.")

