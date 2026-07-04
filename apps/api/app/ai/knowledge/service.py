"""
Nexus AI — RAG Knowledge Service
Central facade managing loading, indexing, caching, and context queries.
"""
from __future__ import annotations
import time
from typing import Dict, Optional

from app.ai.knowledge.models import RetrievalResult
from app.ai.knowledge.loader import DocumentLoader
from app.ai.knowledge.chunking import ChunkManager
from app.ai.knowledge.embeddings import EmbeddingGenerator
from app.ai.knowledge.vector_store import InMemoryVectorStore
from app.ai.knowledge.retriever import RankingEngine

class KnowledgeService:
    """High-level Orchestration facade for RAG pipelines."""
    
    def __init__(
        self,
        embedder: Optional[EmbeddingGenerator] = None,
        store: Optional[InMemoryVectorStore] = None,
        chunk_manager: Optional[ChunkManager] = None
    ):
        self.embedder = embedder or EmbeddingGenerator(dimensions=128)
        self.store = store or InMemoryVectorStore(self.embedder)
        self.chunk_manager = chunk_manager or ChunkManager(chunk_size=500, chunk_overlap=100)
        self._cache: Dict[str, RetrievalResult] = {} # Query cache

    def clear_database(self) -> None:
        """Empties indexed datastores and caches."""
        self.store.clear()
        self._cache.clear()

    def index_document(self, content: str, filename: str, doc_type: str = "TXT") -> int:
        """Parses a text body, partitions into chunks, and saves to the vector index."""
        doc = DocumentLoader.load_from_string(content, filename, doc_type)
        chunks = self.chunk_manager.split_document(doc)
        self.store.add_chunks(chunks)
        # Flush search cache
        self._cache.clear()
        return len(chunks)

    def index_document_from_file(self, filepath: str) -> int:
        """Reads file, chunks content, and saves to indices."""
        doc = DocumentLoader.load_from_filepath(filepath)
        chunks = self.chunk_manager.split_document(doc)
        self.store.add_chunks(chunks)
        self._cache.clear()
        return len(chunks)

    def retrieve_context(self, query: str, limit: int = 3, use_cache: bool = True) -> RetrievalResult:
        """Executes retrieval pipelines, querying cosine similarities and re-ranking matches."""
        # Query Cache Hit
        if use_cache and query in self._cache:
            return self._cache[query]
            
        start_time = time.time()
        raw_matches = self.store.similarity_search(query, k=limit)
        latency = (time.time() - start_time) * 1000
        
        result = RankingEngine.re_rank(query, raw_matches, latency)
        
        if use_cache:
            self._cache[query] = result
        return result
