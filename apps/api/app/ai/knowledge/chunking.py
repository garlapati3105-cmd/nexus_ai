"""
Nexus AI — Chunk Manager
Splits layout documents into chunks with configured character overlap parameters.
"""
from __future__ import annotations
from typing import List
from uuid import uuid4
from app.ai.knowledge.models import KnowledgeDocument, KnowledgeChunk

class ChunkManager:
    """Responsible for text tokenization and overlapping chunk divisions."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_document(self, document: KnowledgeDocument) -> List[KnowledgeChunk]:
        """Divides raw content body into sequential, bounded text chunks."""
        text = document.content
        chunks: List[KnowledgeChunk] = []
        
        if not text:
            return []
            
        start = 0
        idx = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_slice = text[start:end]
            
            chunk_id = f"{document.doc_id}-chunk-{idx}"
            
            chunks.append(
                KnowledgeChunk(
                    chunk_id=chunk_id,
                    doc_id=document.doc_id,
                    text=chunk_slice,
                    index=idx,
                    metadata=document.metadata,
                    embedding=[] # Generated at insertion layer
                )
            )
            
            idx += 1
            if end >= text_length:
                break
            start += (self.chunk_size - self.chunk_overlap)
            
        return chunks
