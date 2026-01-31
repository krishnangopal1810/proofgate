"""
ProofGate Schemas Package

Pydantic models for strict structured outputs from agents.
"""

from .agents import (
    PolicyAgentOutput,
    RiskAgentOutput,
    EvidenceAgentOutput,
    FinalVerdict,
)
from .documents import (
    Document,
    ExcerptBlock,
    RunTrace,
)

__all__ = [
    "PolicyAgentOutput",
    "RiskAgentOutput",
    "EvidenceAgentOutput",
    "FinalVerdict",
    "Document",
    "ExcerptBlock",
    "RunTrace",
]
