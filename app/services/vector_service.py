import os
import re
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import nltk
from nltk.tokenize import sent_tokenize
from nltk.data import find
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from app.pydantics.models import PDFSuccessResponse

load_dotenv()

EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')
CURRENT_EMBEDDING_MODEL = SentenceTransformer(EMBEDDING_MODEL)


class VectorService:
    def __init__(self):
        self.utils_dir = "app/utils"
        self.ensure_utils_directory()
        self.embedding_model = CURRENT_EMBEDDING_MODEL
        self.persist_db = os.getenv('VECTOR_PERSIST', 'False').lower() == 'true'
        self._initialize_chromadb()
        self._ensure_nltk_data()

    def ensure_utils_directory(self):
        """Ensure the utils directory exists"""
        os.makedirs(self.utils_dir, exist_ok=True)

    def _initialize_chromadb(self):
        """Initialize ChromaDB with configurable persistence"""
        try:
            if self.persist_db:
                # Persistent ChromaDB
                persist_directory = os.path.join(os.getcwd(), 'chroma_db')
                os.makedirs(persist_directory, exist_ok=True)

                self.chroma_client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
            else:
                # In-memory ChromaDB
                self.chroma_client = chromadb.EphemeralClient(
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )

            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="pdf_documents",
                metadata={"description": "PDF document chunks for RAG"}
            )

        except Exception as e:
            raise e

    def _ensure_nltk_data(self):
        """Ensure required NLTK data is available"""
        try:
            find("tokenizers/punkt")
            find("tokenizers/punkt/english.pickle")
            find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt")
            nltk.download("punkt_tab")

    def clean_text(self, text: str) -> str:
        """Clean unnecessary spaces, tabs, and invisible characters."""
        text = text.replace("\u200b", "")  # Remove Zero Width Space
        text = re.sub(r"\n+", " ", text)  # Replace multiple newlines with space
        text = re.sub(r"\t+", " ", text)  # Remove tabs
        text = re.sub(r"\s{2,}", " ", text).strip()  # Remove multiple spaces
        return text

    def tokenize_sentences(self, text: str, min_tokens: int = 300, max_tokens: int = 500) -> List[str]:
        """
        Tokenize and split text into chunks based on token limits.

        Args:
            text: Input text to tokenize
            min_tokens: Minimum tokens per chunk
            max_tokens: Maximum tokens per chunk

        Returns:
            List of text chunks
        """
        try:
            sentences = sent_tokenize(text)
            chunks, current_chunk, current_token_count = [], [], 0

            for sentence in sentences:
                token_count = len(sentence.split())

                if current_token_count + token_count > max_tokens:
                    if current_token_count >= min_tokens:
                        chunks.append(" ".join(current_chunk))
                    current_chunk, current_token_count = [sentence], token_count
                else:
                    current_chunk.append(sentence)
                    current_token_count += token_count

            if current_chunk:
                chunks.append(" ".join(current_chunk))

            return chunks

        except Exception as e:
            print(f"Error while tokenizing: {e}")
            return []

    def get_text_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text using SentenceTransformer.

        Args:
            text: Input text to embed

        Returns:
            List of embedding values
        """
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            raise e

    def vectorize_nudge(self, pdf_data: PDFSuccessResponse) -> Dict[str, Any]:
        """
        Process PDF files and store them as vectors in ChromaDB.

        Args:
            pdf_data: Dictionary containing 'pdf_name' and 'total_pages'

        Returns:
            Dict with processing results
        """
        try:
            pdf_name = pdf_data.pdf_filename
            total_pages = pdf_data.total_pages


            # Find PDF directory
            pdf_dir = os.path.join(self.utils_dir, pdf_name)

            if not os.path.exists(pdf_dir):
                raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

            # Read all part files and combine content
            pdf_content = self._read_all_pdf_parts(pdf_dir)

            if not pdf_content.strip():
                raise ValueError(f"No content found in PDF directory: {pdf_dir}")

            # Process and store in ChromaDB
            result = self._process_and_store_chunks(
                pdf_content=pdf_content,
                pdf_name=pdf_name,
                total_pages=total_pages
            )

            return {
                "status": "success",
                "pdf_name": pdf_name,
                "total_pages": total_pages,
                "chunks_created": result['chunks_created'],
                "chunks_stored": result['chunks_stored'],
                "persistence_mode": "persistent" if self.persist_db else "in-memory"
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "pdf_name": pdf_data.pdf_filename
            }

    def _read_all_pdf_parts(self, pdf_dir: str) -> str:
        """
        Read all part files in the PDF directory and combine them.

        Args:
            pdf_dir: Path to PDF directory containing part files

        Returns:
            Combined text content from all parts
        """
        try:
            # Get all part files
            part_files = [f for f in os.listdir(pdf_dir) if f.startswith('part_') and f.endswith('.txt')]
            part_files.sort()  # Ensure proper order

            if not part_files:
                raise ValueError(f"No part files found in directory: {pdf_dir}")

            pdf_content = ""

            # Read each part file
            for part_file in part_files:
                part_path = os.path.join(pdf_dir, part_file)

                with open(part_path, 'r', encoding='utf-8') as f:
                    part_content = f.read()

                # Clean and add to combined content
                cleaned_content = self.clean_text(part_content)
                pdf_content += f"{cleaned_content}\n\n"

            return pdf_content.strip()

        except Exception as e:
            raise e

    def _process_and_store_chunks(self, pdf_content: str, pdf_name: str, total_pages: int) -> Dict[str, int]:
        """
        Process PDF content into chunks and store in ChromaDB.

        Args:
            pdf_content: Combined text content from all PDF parts
            pdf_name: Name of the PDF
            total_pages: Total number of pages in PDF

        Returns:
            Dictionary with processing statistics
        """
        try:
            # Create chunks from the content
            chunks = self.tokenize_sentences(pdf_content)

            if not chunks:
                raise ValueError("No chunks were created from the PDF content")

            chunks_stored = 0

            # Process each chunk
            for chunk_num, chunk_text in enumerate(chunks, 1):
                try:
                    # Generate embedding for the chunk
                    embedding = self.get_text_embedding(chunk_text)

                    # Creating metadata
                    metadata = {
                        "pdf_name": pdf_name,
                        "pdf_len": total_pages,
                        "chunk_num": chunk_num,
                        "total_chunks": len(chunks),
                        "chunk_id": f"{pdf_name}_chunk_{chunk_num:03d}",
                        "created_at": datetime.now(timezone.utc).timestamp(),
                        "content_length": len(chunk_text),
                        "source": "pdf_vectorization"
                    }

                    # Generate unique ID for this chunk
                    chunk_id = f"{pdf_name}_{chunk_num:03d}_{str(uuid.uuid4())[:8]}"

                    # Store in ChromaDB
                    self.collection.add(
                        documents=[chunk_text],
                        embeddings=[embedding],
                        metadatas=[metadata],
                        ids=[chunk_id]
                    )

                    chunks_stored += 1

                except Exception as e:
                    continue

            return {
                "chunks_created": len(chunks),
                "chunks_stored": chunks_stored
            }

        except Exception as e:
            raise e

    def semantic_search(self, query: str, pdf_name: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Search for similar chunks in the vector database.

        Args:
            query: Search query text
            pdf_name: Optional PDF name to filter results
            top_k: Number of results to return

        Returns:
            Dictionary with search results
        """
        try:
            # Generate embedding for the query
            query_embedding = self.get_text_embedding(query)

            where_clause = None
            if pdf_name:
                where_clause = {"pdf_name": pdf_name}

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results['documents'][0]) if results['documents'] else 0
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def delete_pdf_vectors(self, pdf_name: str) -> Dict[str, Any]:
        """
        Delete all vectors for a specific PDF.

        Args:
            pdf_name: Name of the PDF to delete

        Returns:
            Dictionary with deletion results
        """
        try:
            # Get all documents for this PDF
            results = self.collection.get(
                where={"pdf_name": pdf_name},
                include=["metadatas"]
            )

            if not results['ids']:
                return {
                    "success": True,
                    "message": f"No vectors found for PDF: {pdf_name}",
                    "deleted_count": 0
                }

            # Delete the documents
            self.collection.delete(
                where={"pdf_name": pdf_name}
            )

            deleted_count = len(results['ids'])

            return {
                "success": True,
                "message": f"Successfully deleted vectors for PDF: {pdf_name}",
                "deleted_count": deleted_count
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pdf_name": pdf_name
            }

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.

        Returns:
            Dictionary with collection information
        """
        try:
            count = self.collection.count()

            return {
                "success": True,
                "collection_name": self.collection.name,
                "total_documents": count,
                "persistence_mode": "persistent" if self.persist_db else "in-memory",
                "embedding_model": "all-MiniLM-L6-v2"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
