# RAG Pipeline Development Tasks

## Phase 1: Document Upload & Knowledge Base Construction

- [x] **Project Scaffolding**
    - [x] Create project structure from `PRD.md`.
- [x] **Document Processing (`src/rag/utils/document_processor.py`)**
    - [x] Implement file receiving logic for PDF and Word documents.
    - [x] Implement image extraction from documents.
    - [x] Implement local storage for extracted images in `rag/knowledge/images`.
    - [x] Implement image description generation using a multimodal LLM (e.g., `amazon.titan-embed-image-v1`).
    - [x] Implement JSON wrapping for image description and path: `{"description": "...", "imgpath": "..."}`.
    - [x] Implement insertion of `[image_info]` tags into the extracted text.
    - [x] Implement text extraction and cleaning from documents.
    - [x] Implement text splitting using `RecursiveCharacterTextSplitter`.
    - [x] Implement embedding generation for text chunks using `amazon.titan-embed-image-v1`.
- [x] **Vector Store (`src/rag/utils/milvus_manager.py`)**
    - [x] Implement Milvus Lite connection management.
    - [x] Implement Milvus collection creation and schema definition.
    - [x] Implement data insertion logic for text chunks, embeddings, and metadata.
- [x] **API Endpoint (`src/rag/main.py`)**
    - [x] Create a file upload endpoint.
    - [x] Integrate the `document_processor` and `milvus_manager` into the upload endpoint.

## Phase 2: Knowledge Retrieval & Initial Integration

- [x] **Retrieval Logic (`src/rag/utils/retriever.py`)**
    - [x] Implement user query embedding using `amazon.titan-embed-image-v1`.
    - [x] Implement semantic search functionality with Milvus.
    - [x] Implement re-ranking of search results using `cohere.rerank-v3-5:0`.
    - [x] Implement a function to pass the user query and re-ranked context to an LLM (e.g., `claude-3-haiku`) for initial processing.
    - [x] Ensure the LLM is prompted to generate a step-by-step guide from the context.
- [x] **API Endpoint (`src/rag/main.py`)**
    - [x] Create a query endpoint to receive user questions.
    - [x] Integrate the `retriever` logic into the query endpoint.

## Phase 3: Final Report Generation (CrewAI)

- [x] **CrewAI Setup (`src/rag/crew.py`)**
    - [x] Define the "Report Generation" Crew.
    - [x] Define an Agent responsible for refining and formatting (e.g., "Report Writing Expert").
    - [x] Define a Task for the agent to process the step-by-step guide into a polished, user-friendly report.
    - [x] Implement logic to handle `[image_info]` tags and format them for frontend display.
- [x] **Configuration (`src/rag/config/`)**
    - [x] Define the agent's role, goal, and backstory in `agents.yaml`.
    - [x] Define the report generation task in `tasks.yaml`.
- [x] **API Endpoint (`src/rag/main.py`)**
    - [x] Integrate the CrewAI process into the query endpoint.
    - [x] Ensure the final, formatted report from the crew is the ultimate response to the user.

## Phase 4: Testing

- [x] Write unit tests for `document_processor.py`.
- [x] Write unit tests for `milvus_manager.py`.
- [x] Write unit tests for `retriever.py`.
- [x] Write integration tests for the end-to-end file upload and query pipeline.
