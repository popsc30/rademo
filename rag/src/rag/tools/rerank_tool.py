from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import cohere
import os

class RerankToolInput(BaseModel):
    """Input schema for RerankTool."""
    query: str = Field(..., description="The user's query.")
    documents: list = Field(..., description="The list of documents to rerank.")

class RerankTool(BaseTool):
    name: str = "Rerank Documents"
    description: str = "Reranks a list of documents based on a query."
    args_schema: Type[BaseModel] = RerankToolInput

    def _run(self, query: str, documents: list) -> list:
        co = cohere.BedrockClientV2(aws_region="ap-northeast-1")
        rerank_response = co.rerank(
            model="cohere.rerank-v3-5:0",
            query=query,
            documents=documents,
            top_n=min(5, len(documents)),
        )
        
        reranked_docs = []
        for hit in rerank_response.results:
            reranked_docs.append(documents[hit.index])
        return reranked_docs
