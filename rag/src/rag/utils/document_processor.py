import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import List, Dict, Any

import boto3
import docx
from PIL import Image
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger

# Constants
IMAGE_DIR = Path("rag/knowledge/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

class DocumentProcessor:
    """
    Handles the processing of documents, including text and image extraction,
    embedding generation, and preparing data for the knowledge base.
    """

    def __init__(self, mock: bool = False):
        """
        Initializes the DocumentProcessor.

        Args:
            embedding_model_id (str): The ID of the model to use for generating embeddings.
            image_description_model_id (str): The ID of the model for describing images.
            mock (bool): If True, runs in mock mode without actual API calls.
        """
        self.mock = mock
        if not self.mock:
            self.bedrock_client = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "ap-southeast-2"))
        else:
            self.bedrock_client = None
            logger.info("DocumentProcessor running in mock mode.")
            
        self.embedding_model_id = "amazon.titan-embed-image-v1"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Main function to process a single document.

        Args:
            file_path (str): The path to the document to process.

        Returns:
            List[Dict[str, Any]]: A list of processed text chunks with their embeddings.
        """
        logger.info(f"Processing document: {file_path}")
        # 1. Extract text and images
        raw_text, extracted_images = self._extract_text_and_images(file_path)

        # 2. Get descriptions for images and insert placeholders
        processed_text = self._describe_images_and_insert_placeholders(raw_text, extracted_images)

        # 3. Split text into chunks
        text_chunks = self.text_splitter.split_text(processed_text)

        # 4. Generate embeddings for each chunk
        processed_chunks = self._generate_embeddings(text_chunks)

        logger.info(f"Successfully processed {len(processed_chunks)} chunks from {file_path}")
        return processed_chunks

    def _extract_text_and_images(self, file_path: str) -> (str, List[Path]):
        """
        Extracts text and images from a given document (PDF or DOCX).
        Images are saved to the IMAGE_DIR.
        """
        file_extension = Path(file_path).suffix.lower()
        if file_extension == ".pdf":
            return self._extract_from_pdf(file_path)
        elif file_extension == ".docx":
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def _extract_from_pdf(self, file_path: str) -> (str, List[Path]):
        """Extracts text and images from a PDF file using PyMuPDF."""
        logger.info(f"Extracting from PDF: {file_path}")
        text = ""
        image_paths = []
        doc = fitz.open(file_path)

        for page_num, page in enumerate(doc):
            # Extract text
            text += page.get_text()

            # Extract images
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Save the image
                image_ext = base_image["ext"]
                image_filename = f"pdf_{Path(file_path).stem}_p{page_num+1}_img{img_index+1}.{image_ext}"
                img_save_path = IMAGE_DIR / image_filename
                
                with open(img_save_path, "wb") as img_file:
                    img_file.write(image_bytes)
                image_paths.append(img_save_path)
                
                # Add a placeholder in the text for the image
                text += f"\n[image_placeholder:{img_save_path}]\n"

        doc.close()
        logger.info(f"Extracted {len(image_paths)} images from {file_path}")
        return text, image_paths

    def _extract_from_docx(self, file_path: str) -> (str, List[Path]):
        """Extracts text and images from a DOCX file."""
        logger.info(f"Extracting from DOCX: {file_path}")
        doc = docx.Document(file_path)
        text = ""
        image_paths = []
        
        # Keep track of image index
        img_index = 0

        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                img_index += 1
                image_bytes = rel.target_part.blob
                
                # Determine image extension
                image_ext = rel.target_part.content_type.split('/')[-1]
                if image_ext == "jpeg":
                    image_ext = "jpg"
                
                image_filename = f"docx_{Path(file_path).stem}_img{img_index}.{image_ext}"
                img_save_path = IMAGE_DIR / image_filename

                with open(img_save_path, "wb") as img_file:
                    img_file.write(image_bytes)
                image_paths.append(img_save_path)
                text += f"\n[image_placeholder:{img_save_path}]\n"

        for para in doc.paragraphs:
            text += para.text + "\n"
            
        logger.info(f"Extracted {len(image_paths)} images from {file_path}")
        logger.warning(f"Extracted text: {text}")
        return text, image_paths

    def _describe_images_and_insert_placeholders(self, text: str, image_paths: List[Path]) -> str:
        """
        Generates descriptions for images and replaces placeholders in the text.
        """
        if not image_paths:
            return text

        logger.info(f"Describing {len(image_paths)} images...")
        for img_path in image_paths:
            description = self._get_image_description(img_path)
            image_info = {
                "description": description,
                "imgpath": str(img_path.resolve())
            }
            info_str = f"[image_info]{json.dumps(image_info)}[/image_info]"
            
            # Replace the corresponding placeholder
            placeholder = f"[image_placeholder:{img_path}]"
            text = text.replace(placeholder, info_str)
            
        return text

    def _get_image_description(self, img_path: Path) -> str:
        """
        Generates a text description for a single image using a multimodal LLM.
        """
        if self.mock:
            logger.info(f"Getting description for {img_path} (mock)...")
            return f"A mock description for the image at {img_path}."

        logger.info(f"Getting description for {img_path} (real)...")
        try:
            with open(img_path, "rb") as image_file:
                image_bytes = image_file.read()

            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            
            content = [
                {
                    "image": {
                        "format": "png",
                        "source": { "bytes": base64_image }
                    }
                },
                {"text": "Describe this image in detail."}
            ]
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 300,
                    "temperature": 0.5,
                    "top_p": 0.9
                }
            }
            response_body = self._invoke_bedrock("apac.amazon.nova-lite-v1:0", request_body)
            return response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')

        except Exception as e:
            logger.exception(f"Error getting description for {img_path}: {e}")
            return f"Error describing image: {e}"

    def _generate_embeddings(self, text_chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Generates vector embeddings for a list of text chunks using Bedrock.
        """
        if self.mock:
            logger.info(f"Generating embeddings for {len(text_chunks)} chunks (mock)...")
            processed_chunks = []
            for chunk in text_chunks:
                embedding = [0.0] * 1536 # Titan embedding dimension
                processed_chunks.append({"text": chunk, "embedding": embedding, "metadata": {}})
            return processed_chunks

        logger.info(f"Generating embeddings for {len(text_chunks)} chunks (real)...")
        processed_chunks = []
        for chunk in text_chunks:
            try:
                # Determine the correct input key based on the model name
                if 'image' in self.embedding_model_id:
                    body = json.dumps({"inputImage": chunk}) # This is illustrative; text chunks shouldn't be passed to image models
                else:
                    body = json.dumps({"inputText": chunk})

                response = self.bedrock_client.invoke_model(
                    body=body,
                    modelId=self.embedding_model_id,
                    accept="application/json",
                    contentType="application/json"
                )
                response_body = json.loads(response.get("body").read())
                embedding = response_body.get("embedding")
                processed_chunks.append({
                    "text": chunk,
                    "embedding": embedding,
                    "metadata": {} 
                })
            except Exception as e:
                logger.exception(f"Error generating embedding for chunk: {e}")
                continue
        return processed_chunks
    
    def _invoke_bedrock(self, model_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Generic method to invoke a Bedrock model without retry logic."""
        try:
            response = self.bedrock_client.invoke_model(
                body=json.dumps(body),
                modelId=model_id,
                contentType='application/json',
                accept='application/json'
            )
            return json.loads(response.get('body').read())
        except Exception as e:
            logger.error(f"A Bedrock client error occurred when invoking {model_id}: {e}")
            raise

if __name__ == '__main__':
    # Example usage for testing purposes
    # This requires creating a dummy file, e.g., dummy.txt
    logger.info("Running document processor example...")
    processor = DocumentProcessor()
    dummy_file = "dummy.txt"
    with open(dummy_file, "w") as f:
        f.write("This is a test document. It contains text and references to images.")

    # Since we don't have real PDFs/DOCX with images yet, this will be simple.
    # The full implementation will require more complex test cases.
    try:
        # We need to adapt this to work with a simple txt file for now
        raw_text, _ = processor._extract_text_and_images(dummy_file)
        text_chunks = processor.text_splitter.split_text(raw_text)
        processed_data = processor._generate_embeddings(text_chunks)
        logger.info(f"Processed data: {processed_data}")
    except ValueError as e:
        logger.exception(f"Caught expected error for unsupported file type: {e}")

    # Clean up the dummy file
    os.remove(dummy_file)
    logger.info("Example run finished.")
