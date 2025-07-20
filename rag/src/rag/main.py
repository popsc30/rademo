import argparse
import warnings
from dotenv import load_dotenv
from loguru import logger

from rag.crew import RagCrew
from rag.utils.document_processor import DocumentProcessor
from rag.utils.logging_config import setup_logging
from rag.utils.milvus_manager import MilvusManager
from rag.utils.retriever import Retriever

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

load_dotenv()



def train_internal(file_path: str, mock: bool = False):
    """
    Processes a document and adds it to the knowledge base.
    """
    logger.info(f"Starting training process for file: {file_path}")
    try:
        doc_processor = DocumentProcessor(mock=mock)
        milvus_manager = MilvusManager()
        processed_chunks = doc_processor.process_document(file_path)
        if processed_chunks:
            milvus_manager.insert_data(processed_chunks)
            logger.info(f"Successfully trained on {file_path}")
        else:
            logger.warning(f"No chunks were processed from {file_path}. Training skipped.")
    except Exception as e:
        logger.exception(f"An error occurred during training: {e}")


def run(query: str, mock: bool = False):
    """
    Run the RAG system with a user query.
    """
    logger.info(f"Received query: '{query}'")
    try:
        milvus_manager = MilvusManager()
        retriever = Retriever(milvus_manager, mock=mock)
        documents = retriever.retrieve(query)
        logger.info(f"Documents: {documents}")

        if mock:
            logger.info("CrewAI execution skipped in mock mode.")
            final_report = "This is a mock report."
        else:
            logger.info("Passing documents to CrewAI for final report generation...")
            inputs = {
                'topic': query,
                'documents': documents,
            }
            final_report = RagCrew().crew().kickoff(inputs=inputs)
        
        logger.info("\n--- Final Report ---")
        logger.info(final_report)
        logger.info("--------------------\n")

    except Exception as e:
        logger.exception(f"An error occurred while running the query: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    query = "What the company's policy?"
    try:
        milvus_manager = MilvusManager()
        retriever = Retriever(milvus_manager)
        documents = retriever.retrieve(query)

        logger.info("Passing documents to CrewAI for final report generation...")
        inputs = {
            'topic': query,
            'documents': documents,
        }
        # final_report = RagCrew().crew().kickoff(inputs=inputs)
        import sys
        RagCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

        logger.info("--------------------\n")
    
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def serve():
    """
    Serves the RAG Crew API using uvicorn.
    """
    import uvicorn
    logger.info("Starting the RAG Crew API server...")
    uvicorn.run("rag.api:app", host="0.0.0.0", port=8002, reload=True)

def main():
    """
    Main entry point to run the RAG system from the command line.
    """
    setup_logging()
    parser = argparse.ArgumentParser(description="A RAG system powered by CrewAI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-parser for the 'train' command
    train_parser = subparsers.add_parser("train", help="Train the RAG system by processing a document.")
    train_parser.add_argument("file", type=str, help="The absolute path to the document file to process.")
    train_parser.add_argument("--mock", action="store_true", help="Run in mock mode without actual API calls.")

    # Sub-parser for the 'run' command
    run_parser = subparsers.add_parser("run", help="Run the RAG system with a query.")
    run_parser.add_argument("query", type=str, help="The user query to process.")
    run_parser.add_argument("--mock", action="store_true", help="Run in mock mode without actual API calls.")

    # Sub-parser for the 'reset-db' command
    reset_parser = subparsers.add_parser("reset-db", help="Reset the Milvus database by dropping the collection.")

    # Sub-parser for the 'serve' command
    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI server.")

    args = parser.parse_args()

    if args.command == "train":
        train_internal(args.file, mock=args.mock)
    elif args.command == "run":
        run(args.query, mock=args.mock)
    elif args.command == "reset-db":
        try:
            milvus_manager = MilvusManager()
            milvus_manager.reset_collection()
        except Exception as e:
            logger.exception(f"An error occurred while resetting the database: {e}")
    elif args.command == "serve":
        serve()


if __name__ == "__main__":
    main()
