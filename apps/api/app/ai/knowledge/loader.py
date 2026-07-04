"""
Nexus AI — Document Loader
Simple document parser loading PDF, DOCX, TXT, and Markdown payloads.
"""
from __future__ import annotations
import os
from uuid import uuid4
import datetime
from app.ai.knowledge.models import KnowledgeDocument, KnowledgeMetadata

class DocumentLoader:
    """Loads text documents from raw inputs and file paths."""
    
    @staticmethod
    def load_from_string(content: str, filename: str, doc_type: str = "TXT") -> KnowledgeDocument:
        """Loads a document using raw text contents."""
        name_extracted = os.path.basename(filename)
        doc_id = f"doc-{uuid4().hex[:8].upper()}"
        
        meta = KnowledgeMetadata(
            source=filename,
            doc_type=doc_type.upper(),
            created_at=datetime.datetime.utcnow().isoformat()
        )
        
        return KnowledgeDocument(
            doc_id=doc_id,
            title=name_extracted,
            content=content,
            metadata=meta
        )

    @classmethod
    def load_from_filepath(cls, filepath: str) -> KnowledgeDocument:
        """Reads file payload from local path."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source file {filepath} not found.")
            
        ext = os.path.splitext(filepath)[1].lower().replace(".", "")
        doc_type = "TXT"
        if ext in ["md", "markdown"]:
            doc_type = "MD"
        elif ext in ["pdf", "docx"]:
            doc_type = ext.upper()
            
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        return cls.load_from_string(content, filepath, doc_type)
