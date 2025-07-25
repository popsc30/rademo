import os
import boto3
import json
import cohere
from loguru import logger
from .milvus_manager import MilvusManager

class Retriever:
    """
    Handles the retrieval of relevant documents from the knowledge base,
    re-ranking, and initial synthesis of the answer.
    """

    def __init__(self, milvus_manager: MilvusManager, mock: bool = False):
        """
        Initializes the Retriever.

        Args:
            milvus_manager (MilvusManager): An instance of the MilvusManager.
            mock (bool): If True, runs in mock mode without actual API calls.
        """
        self.mock = mock
        self.milvus_manager = milvus_manager
        self.embedding_model_id = os.environ.get("EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
        self.llm_model_id = os.environ.get("CONTENT_STRUCTURING_MODEL")
        self.rerank_model_id = os.environ.get("RERANK_MODEL")

        if not self.mock:
            self.bedrock_client = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION"))
        else:
            self.bedrock_client = None
            logger.info("Retriever running in mock mode.")

    def retrieve(self, query: str, top_n: int = 50) -> list:
        """
        Embeds a query, retrieves the top_n most relevant document chunks from Milvus,
        and then reranks them for relevance.

        Args:
            query (str): The user's query.
            top_n (int): The number of documents to retrieve.

        Returns:
            list: A list of reranked document chunks.
        """
        logger.info(f"Embedding query and retrieving documents for: '{query}'")
        query_embedding = self._embed_query(query)
        search_results = self._search_milvus(query_embedding, top_n=top_n)
        logger.info(f"search_results type: {type(search_results)}, value: {search_results}")
        
        if not search_results:
            return []

        # Robustly convert Hits/SequenceIterator to list

        results = []
        for hit in search_results:
            results.append(hit.entity)

        if self.mock:
            logger.info("Skipping reranking in mock mode.")
            return results[:5]

        return self._rerank_documents(query, results)

    def _rerank_documents(self, query: str, results: list, threshold: float = 0.1) -> list:
        """
        Reranks the retrieved results using Cohere's rerank model and filters
        them based on a relevance threshold.
        """
        logger.info("Reranking documents...")
        documents = []
        for result in results:
            documents.append(result.get('text'))
            logger.info(f": type: {type(result.get('text'))}, value: {result.get('text')}")
        try:
            co = cohere.BedrockClientV2(aws_region="ap-northeast-1")


            rerank_response = co.rerank(
                model="cohere.rerank-v3-5:0",
                query=query,
                documents=documents,
                top_n=min(5, len(documents)),
            )
            
            reranked_docs = []
            for hit in rerank_response.results:
                if hit.relevance_score >= threshold:
                    reranked_docs.append(documents[hit.index])
                    logger.info(f"  - Document (index {hit.index}) is relevant with score {hit.relevance_score:.4f}")
                else:
                    logger.warning(f"  - Document (index {hit.index}) is IRRELEVANT with score {hit.relevance_score:.4f}. Filtering out.")

            logger.info(f"Reranked and filtered {len(reranked_docs)} documents from an initial {len(documents)}.")
            return reranked_docs
        except Exception as e:
            logger.exception(f"Error reranking documents: {e}")
            # Fallback to returning the original documents if reranking fails
            return documents[:5]

    def _embed_query(self, query: str) -> list:
        """
        Embeds the user's query using the specified Bedrock embedding model.
        """
        if self.mock:
            logger.info("Embedding query (mock)...")
            return [0.0] * 1024 # Titan text embedding dimension

        logger.info("Embedding query (real)...")
        try:
            body = json.dumps({"inputText": query})
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId=self.embedding_model_id,
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get("body").read())
            return response_body.get("embedding")
        except Exception as e:
            logger.exception(f"Error embedding query: {e}")
            return None

    def _search_milvus(self, query_embedding: list, top_n: int) -> list:
        """
        Searches the Milvus collection for the most relevant document chunks.
        """
        if not query_embedding:
            logger.warning("No query embedding provided. Skipping search.")
            return []
            
        logger.info(f"Searching Milvus for top {top_n} results...")
        try:
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10},
            }
            results = self.milvus_manager.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_n,
                output_fields=["text", "metadata"]
            )

            return results[0]  # search returns a list of results for each query
        except Exception as e:
            logger.exception(f"Error searching Milvus: {e}")
            return []

    


if __name__ == '__main__':
    # Example usage for testing purposes
    logger.info("Running retriever example...")
    try:
        # This requires a running Milvus instance with some data.
        # For this example, we'll mock the MilvusManager.
        class MockMilvusManager:
            def __init__(self):
                logger.info("Initialized MockMilvusManager.")
            def search(self, *args, **kwargs):
                return []

        retriever = Retriever(milvus_manager=MockMilvusManager())
        
        test_query = "How do I file an expense report?"
        guide = retriever.retrieve_and_synthesize(test_query)
        
        logger.info("\n--- Synthesized Guide ---")
        logger.info(guide)
        logger.info("\nRetriever example finished.")

    except Exception as e:
        logger.exception(f"An error occurred during the retriever example: {e}")
        logger.error("Please ensure you have your AWS and Cohere credentials configured.")

