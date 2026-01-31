"""
ProofGate Guards Package

Citation whitelist enforcement and validation guards.
"""

from .citation_whitelist import (
    validate_citations,
    CitationValidationError,
)

__all__ = [
    "validate_citations",
    "CitationValidationError",
]
