"""
Nexus AI — In-Memory Vector Store
Lightweight database index computing cosine similarity matches on normalized chunks.
"""
from __future__ import annotations
from typing import List, Tuple
from app.ai.knowledge.models import KnowledgeChunk
from app.ai.knowledge.embeddings import EmbeddingGenerator

class InMemoryVectorStore:
    """In-memory indexing store resolving cosine vector evaluations."""
    
    def __init__(self, embedder: EmbeddingGenerator):
        self.embedder = embedder
        self._store: List[KnowledgeChunk] = []

    def clear(self) -> None:
        """Wipes matching catalog items."""
        self._store.clear()

    def add_chunks(self, chunks: List[KnowledgeChunk]) -> None:
        """Indexes matching texts, updating embedding vectors concurrently."""
        for chunk in chunks:
            if not chunk.embedding:
                chunk.embedding = self.embedder.generate(chunk.text)
            self._store.append(chunk)

    def similarity_search(self, query: str, k: int = 3) -> List[Tuple[KnowledgeChunk, float]]:
        """Scores candidate chunks based on cosine distance parameters."""
        query_vector = self.embedder.generate(query)
        scored_candidates: List[Tuple[KnowledgeChunk, float]] = []
        
        for candidate in self._store:
            similarity = self._cosine_similarity(query_vector, candidate.embedding)
            # Clip between [0.0, 1.0] for model format safety
            norm_score = max(0.0, min(1.0, (similarity + 1.0) / 2.0))
            scored_candidates.append((candidate, norm_score))
            
        # Return sorted by highest similarity
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:k]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        sum1 = sum(a*a for a in v1)
        sum2 = sum(b*b for b in v2)
        norm = (sum1 * sum2) ** 0.5
        return dot / norm if norm > 0 else 0.0
