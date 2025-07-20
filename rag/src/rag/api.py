import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger


from rag.crew import RagCrew
from rag.utils.document_processor import DocumentProcessor
from rag.utils.logging_config import setup_logging
from rag.utils.milvus_manager import MilvusManager
from rag.utils.retriever import Retriever

# Initialize FastAPI app
app = FastAPI(
    title="RAG Crew API",
    description="An API for processing documents and answering questions using a RAG-based CrewAI.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Setup logging
setup_logging()

class QueryRequest(BaseModel):
    """Request model for the /query endpoint."""
    query: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a document (.pdf or .docx), processes it, and adds it to the knowledge base.
    """
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a .pdf or .docx file.")

    try:
        # Use a temporary directory to securely handle the file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / file.filename
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File '{file.filename}' uploaded to temporary path: {temp_path}")

            # Process the document
            doc_processor = DocumentProcessor()
            milvus_manager = MilvusManager()
            processed_chunks = doc_processor.process_document(str(temp_path))
            
            if processed_chunks:
                milvus_manager.insert_data(processed_chunks)
                logger.info(f"Successfully processed and stored '{file.filename}' in the knowledge base.")
                return {"message": f"File '{file.filename}' uploaded and processed successfully."}
            else:
                logger.warning(f"No content could be processed from '{file.filename}'.")
                raise HTTPException(status_code=400, detail="No content could be processed from the file.")

    except Exception as e:
        logger.exception(f"An error occurred during file upload and processing: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
    finally:
        # Ensure the file stream is closed
        file.file.close()

@app.post("/query")
async def query_rag(request: QueryRequest):
    """
    Receives a query, retrieves relevant documents, and generates a report using the RAG crew.
    """
    try:
        logger.info(f"Received query: '{request.query}'")
        
        # Retrieve documents
        milvus_manager = MilvusManager()
        retriever = Retriever(milvus_manager)
        documents = retriever.retrieve(request.query)
        
        if not documents:
            logger.warning("No relevant documents found for the query.")
            return {"answer": "I could not find any relevant documents to answer your question. Please try uploading more documents or rephrasing your query."}

        logger.info(f"Retrieved {len(documents)} documents for the query.")
        logger.info(f"Documents: {documents}")

        # Run the crew to get the final report
        inputs = {
            'topic': request.query,
            'documents': documents,
        }
        final_report = RagCrew().crew().kickoff(inputs=inputs)
        
        # Return the final report along with the source documents
        return {
            "answer": {final_report["raw"]},
            "meta": {
                "documents": documents
            }
        }

    except Exception as e:
        logger.exception(f"An error occurred during the query process: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/")
def read_root():
    """
A welcome message to verify the API is running.
    """
    return {"message": "Welcome to the RAG Crew API!"}
