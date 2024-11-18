import chromadb
from chromadb.config import Settings
from typing import List, Optional, Dict, Any
import logging
import time
from contextlib import contextmanager

class KnowledgeBase:
    def __init__(self, persist_directory: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.persist_directory = persist_directory
        self._initialize_client()
        self._initialize_collection()

    def _initialize_client(self) -> None:
        """Initialize ChromaDB client with retry mechanism"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                settings = Settings(
                    persist_directory=self.persist_directory,
                    anonymized_telemetry=False
                )
                self.client = chromadb.Client(settings)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to initialize ChromaDB client: {e}")
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2

    def _initialize_collection(self) -> None:
        """Initialize or get the collection with error handling"""
        try:
            self.collection = self.client.get_or_create_collection(
                name="agent_knowledge",
                metadata={"description": "Agent knowledge base"}
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize collection: {e}")
            raise

    @contextmanager
    def error_handling(self, operation: str):
        """Context manager for error handling"""
        try:
            yield
        except Exception as e:
            self.logger.error(f"Error during {operation}: {e}")
            raise

    def add_knowledge(self, documents: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Add documents to knowledge base with validation"""
        if not documents:
            raise ValueError("Documents list cannot be empty")

        with self.error_handling("adding knowledge"):
            ids = [f"doc_{i}_{int(time.time())}" for i in range(len(documents))]
            
            if metadata is None:
                metadata = [{"timestamp": time.time()} for _ in documents]
            
            self.collection.add(
                documents=documents,
                metadatas=metadata,
                ids=ids
            )
            return True

    def retrieve_context(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve context with validation and error handling"""
        if not query or not isinstance(query, str):
            raise ValueError("Invalid query")
        if top_k < 1:
            raise ValueError("top_k must be positive")

        with self.error_handling("retrieving context"):
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            return results['documents'][0] if results['documents'] else []

    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # Implement any necessary cleanup
            pass
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the knowledge base"""
        with self.error_handling("deleting document"):
            self.collection.delete(ids=[doc_id])
            return True

    def update_document(self, doc_id: str, new_content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a document in the knowledge base"""
        with self.error_handling("updating document"):
            self.collection.update(
                ids=[doc_id],
                documents=[new_content],
                metadatas=[metadata] if metadata else None
            )
            return True
