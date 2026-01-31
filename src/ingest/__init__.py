"""
ProofGate Ingest Package

Document loading and chunking with stable excerpt IDs.
"""

from .loader import (
    load_document,
    load_all_documents,
    parse_excerpts_from_document,
)

__all__ = [
    "load_document",
    "load_all_documents",
    "parse_excerpts_from_document",
]
