import shutil
import tempfile
import json
import asyncio
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


from rag.crew import RagCrew
from rag.utils.document_processor import DocumentProcessor
from rag.utils.logging_config import setup_logging
from rag.utils.milvus_manager import MilvusManager
from rag.utils.retriever import Retriever
from loguru import logger


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

@app.post("/query/stream")
async def query_rag_stream(request: QueryRequest):
    """
    Receives a query and returns a streaming response with step-by-step progress updates.
    """
    async def generate_steps():
        try:
            logger.info(f"Starting streaming query: '{request.query}'")
            
            # Step 1: Document Retrieval
            yield f"data: {json.dumps({'step': 'retrieving', 'message': 'Searching for relevant documents...'})}\n\n"
            await asyncio.sleep(0.1)  # Small delay for better UX
            
            milvus_manager = MilvusManager()
            retriever = Retriever(milvus_manager)
            documents = retriever.retrieve(request.query)
            
            yield f"data: {json.dumps({'step': 'retrieved', 'message': f'Found {len(documents)} relevant documents', 'count': len(documents)})}\n\n"
            await asyncio.sleep(0.1)
            
            if len(documents) == 0:
                yield f"data: {json.dumps({'step': 'complete', 'message': 'No relevant documents found. Please try uploading more documents or rephrasing your query.', 'result': 'No relevant documents found.'})}\n\n"
                return
            
            logger.info(f"Retrieved {len(documents)} documents for streaming query.")
            
            # Step 2: AI Analysis
            yield f"data: {json.dumps({'step': 'analyzing', 'message': 'Analyzing document content with AI agents...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Step 3: Report Generation  
            yield f"data: {json.dumps({'step': 'generating', 'message': 'Generating comprehensive report...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Call CrewAI (this is where the actual work happens)
            inputs = {
                'topic': request.query,
                'documents': documents,
            }
            final_report = RagCrew().crew().kickoff(inputs=inputs)
            
            # Step 4: Complete
            yield f"data: {json.dumps({'step': 'complete', 'message': 'Analysis complete', 'result': str(final_report.raw), 'meta': {'documents': documents}})}\n\n"
            
        except Exception as e:
            logger.exception(f"An error occurred during streaming query: {e}")
            yield f"data: {json.dumps({'step': 'error', 'message': f'Error occurred: {str(e)}'})}\n\n"
    
    return StreamingResponse(generate_steps(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Cache-Control"
    })

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
