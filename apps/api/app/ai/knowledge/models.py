"""
Nexus AI — RAG Knowledge Models
Defines schema constraints for Documents, Chunks, and Similarity retrievals.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class KnowledgeMetadata(BaseModel):
    source: str
    doc_type: str # "PDF" | "DOCX" | "TXT" | "MD"
    author: Optional[str] = None
    created_at: Optional[str] = None
    custom_tags: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeDocument(BaseModel):
    doc_id: str
    title: str
    content: str
    metadata: KnowledgeMetadata

class KnowledgeChunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    index: int
    metadata: KnowledgeMetadata
    embedding: List[float] = Field(default_factory=list)

class RetrievalMatch(BaseModel):
    chunk: KnowledgeChunk
    source_document: str # Title / ID reference
    similarity_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)

class RetrievalResult(BaseModel):
    query: str
    matches: List[RetrievalMatch]
    total_matches_found: int
    latency_ms: float = 0.0
