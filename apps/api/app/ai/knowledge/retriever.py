"""
Nexus AI — Knowledge Retriever & Ranker
Retrieves matching chunks and computes explainability confidence scores.
"""
from __future__ import annotations
import time
from typing import List, Tuple

from app.ai.knowledge.models import KnowledgeChunk, RetrievalMatch, RetrievalResult
from app.ai.knowledge.vector_store import InMemoryVectorStore

class RankingEngine:
    """Re-ranks and formats vector search elements into compliant API structures."""
    
    @staticmethod
    def re_rank(
        query: str, 
        raw_matches: List[Tuple[KnowledgeChunk, float]], 
        latency_ms: float
    ) -> RetrievalResult:
        """Converts raw cosine search arrays into structured RetrievalResult output objects."""
        matches: List[RetrievalMatch] = []
        
        for chunk, score in raw_matches:
            # Under mock embeddings, similarity score maps directly to confidence
            match = RetrievalMatch(
                chunk=chunk,
                source_document=chunk.metadata.source,
                similarity_score=score,
                confidence=score
            )
            matches.append(match)
            
        return RetrievalResult(
            query=query,
            matches=matches,
            total_matches_found=len(matches),
            latency_ms=latency_ms
        )
