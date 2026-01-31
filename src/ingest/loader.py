"""
Document Loader

Load and parse documents with stable excerpt IDs.
Documents must have pre-defined [CITE=XXX-###] markers.
"""

import re
import hashlib
from pathlib import Path
from typing import List, Optional

from src.schemas.documents import Document, ExcerptBlock


# Regex to extract cite tokens and their content
CITE_PATTERN = re.compile(
    r'\[CITE=([A-Z]{3}-\d{3})\]\s*\n(.*?)(?=\[CITE=|\Z)',
    re.DOTALL
)


def load_document(
    path: Path,
    doc_type: str,
    doc_id: Optional[str] = None
) -> Document:
    """
    Load a document from disk.
    
    Args:
        path: Path to the document file
        doc_type: Type of document (policy, contract, evidence)
        doc_id: Optional explicit document ID (defaults to filename)
    
    Returns:
        Document object with content and hash
    """
    content = path.read_text(encoding='utf-8')
    
    return Document(
        doc_id=doc_id or path.stem,
        doc_type=doc_type,
        title=_extract_title(content) or path.stem,
        content=content,
    )


def _extract_title(content: str) -> Optional[str]:
    """Extract title from markdown heading."""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return None


def parse_excerpts_from_document(doc: Document) -> List[ExcerptBlock]:
    """
    Parse a document into excerpt blocks using [CITE=XXX-###] markers.
    
    Args:
        doc: Document to parse
    
    Returns:
        List of ExcerptBlock objects with stable IDs
    """
    excerpts = []
    
    for match in CITE_PATTERN.finditer(doc.content):
        excerpt_id = match.group(1)
        text = match.group(2).strip()
        
        # Clean up the text - remove trailing dashes and extra whitespace
        text = re.sub(r'\n---\s*$', '', text).strip()
        
        excerpts.append(ExcerptBlock.create(
            excerpt_id=excerpt_id,
            doc_id=doc.doc_id,
            doc_type=doc.doc_type,
            text=text
        ))
    
    return excerpts


def load_all_documents(data_dir: Path) -> dict:
    """
    Load all documents from the data directory.
    
    Returns:
        Dict with 'documents' list and 'excerpts' dict by type
    """
    docs_dir = data_dir / "docs"
    
    # Document type mapping based on filename prefix
    type_mapping = {
        'policy': 'policy',
        'contract': 'contract',
        'evidence': 'evidence',
    }
    
    documents = []
    excerpts_by_type = {
        'policy': [],
        'contract': [],
        'evidence': [],
    }
    
    for file_path in docs_dir.glob("*.md"):
        # Determine doc type from filename
        doc_type = 'evidence'  # default
        for prefix, dtype in type_mapping.items():
            if file_path.stem.startswith(prefix):
                doc_type = dtype
                break
        
        doc = load_document(file_path, doc_type)
        documents.append(doc)
        
        # Parse excerpts
        doc_excerpts = parse_excerpts_from_document(doc)
        excerpts_by_type[doc_type].extend(doc_excerpts)
    
    return {
        'documents': documents,
        'excerpts': excerpts_by_type,
        'all_excerpts': [
            e for excerpts in excerpts_by_type.values() 
            for e in excerpts
        ]
    }


def get_allowed_citations(excerpts: List[ExcerptBlock]) -> set:
    """Get the set of allowed citation IDs from excerpts."""
    return {e.excerpt_id for e in excerpts}
