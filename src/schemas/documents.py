"""
Document and Trace Schemas

Pydantic models for documents, excerpts, and run traces.
"""

from typing import Literal, List, Dict, Optional
from pydantic import BaseModel, Field
import hashlib


class Document(BaseModel):
    """A source document (policy, contract, or evidence)."""
    doc_id: str = Field(description="Unique document identifier")
    doc_type: Literal["policy", "contract", "evidence"] = Field(
        description="Type of document"
    )
    title: str = Field(description="Human-readable document title")
    content: str = Field(description="Full document content")
    content_hash: str = Field(
        default="",
        description="SHA256 hash of content for integrity checking"
    )
    
    def model_post_init(self, __context) -> None:
        """Compute content hash after initialization."""
        if not self.content_hash and self.content:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()


class ExcerptBlock(BaseModel):
    """
    A chunk of a document with a stable cite token.
    
    Excerpts are the atomic units that agents can cite.
    Example: [CITE=POL-004] indicates excerpt POL-004.
    """
    excerpt_id: str = Field(
        description="Stable excerpt ID (e.g., POL-004, CON-002, EVI-001)"
    )
    cite_token: str = Field(
        description="Formatted citation token (e.g., [CITE=POL-004])"
    )
    doc_id: str = Field(description="Parent document ID")
    doc_type: Literal["policy", "contract", "evidence"] = Field(
        description="Type inherited from parent document"
    )
    text: str = Field(description="Excerpt content text")
    
    @classmethod
    def create(cls, excerpt_id: str, doc_id: str, doc_type: str, text: str) -> "ExcerptBlock":
        """Factory method to create an excerpt with proper cite token."""
        return cls(
            excerpt_id=excerpt_id,
            cite_token=f"[CITE={excerpt_id}]",
            doc_id=doc_id,
            doc_type=doc_type,
            text=text
        )


class RunTrace(BaseModel):
    """
    Trace of a single ProofGate run for auditability and replay.
    
    Enables deterministic replay: same inputs → same outputs.
    """
    run_id: str = Field(description="Unique run identifier (UUID)")
    input_hash: str = Field(
        description="SHA256 hash of (question + excerpt_ids + prompt_versions)"
    )
    question: str = Field(description="The user's original question")
    excerpt_ids: List[str] = Field(
        description="IDs of excerpts used in this run"
    )
    prompt_versions: Dict[str, str] = Field(
        description="Mapping of agent name to prompt version (e.g., {'policy': 'v1'})"
    )
    agent_output_hashes: Dict[str, str] = Field(
        default_factory=dict,
        description="SHA256 hash of each agent's output"
    )
    final_output_hash: str = Field(
        default="",
        description="SHA256 hash of the final verdict"
    )
    replayed: bool = Field(
        default=False,
        description="True if this result was retrieved from cache"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO timestamp of the run"
    )
    latency_ms: Optional[int] = Field(
        default=None,
        description="Total pipeline latency in milliseconds"
    )
    
    @staticmethod
    def compute_input_hash(
        question: str,
        excerpt_ids: List[str],
        prompt_versions: Dict[str, str]
    ) -> str:
        """Compute deterministic hash for caching/replay."""
        sorted_excerpts = ",".join(sorted(excerpt_ids))
        sorted_prompts = ",".join(f"{k}:{v}" for k, v in sorted(prompt_versions.items()))
        payload = f"{question}|{sorted_excerpts}|{sorted_prompts}"
        return hashlib.sha256(payload.encode()).hexdigest()
