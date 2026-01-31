"""
Agent Output Schemas

Pydantic models defining structured outputs for all ProofGate agents.
These ensure JSON schema validation and type safety.
"""

from typing import Literal, List
from pydantic import BaseModel, Field


class PolicyAgentOutput(BaseModel):
    """
    Output from the Policy Agent - the permissive interpreter.
    
    This agent finds ways to say YES while identifying necessary conditions.
    Objective: Permissive interpretation of policy and contract clauses.
    """
    stance: Literal["YES", "YES_CONDITIONAL", "NO"] = Field(
        description="Agent's position on whether the action is allowed by policy"
    )
    conditions: List[str] = Field(
        default_factory=list,
        description="Conditions that must be true for approval"
    )
    rationale: str = Field(
        description="Explanation for the stance, citing specific policy clauses"
    )
    citations: List[str] = Field(
        default_factory=list,
        description="List of excerpt IDs cited (e.g., POL-001, CON-002). ONLY cite provided excerpts."
    )


class RiskAgentOutput(BaseModel):
    """
    Output from the Risk Agent - the conservative guardian.
    
    This agent finds audit landmines and reasons to say NO.
    Objective: Identify risks, reversals, and hard-stop violations.
    """
    stance: Literal["YES", "YES_CONDITIONAL", "NO"] = Field(
        description="Agent's position considering risk factors"
    )
    risk_flags: List[str] = Field(
        default_factory=list,
        description="Warning signs and potential issues found"
    )
    hard_stops: List[str] = Field(
        default_factory=list,
        description="Absolute blockers that prevent approval regardless of other factors"
    )
    rationale: str = Field(
        description="Explanation of risk assessment"
    )
    citations: List[str] = Field(
        default_factory=list,
        description="List of excerpt IDs cited. ONLY cite provided excerpts."
    )


class EvidenceAgentOutput(BaseModel):
    """
    Output from the Evidence Agent - the strict verifier.
    
    This agent demands proof for every claim and fails closed on missing evidence.
    Objective: Verify that documented proof exists for all required facts.
    """
    stance: Literal["SUFFICIENT", "PARTIAL", "MISSING"] = Field(
        description="Assessment of evidence sufficiency"
    )
    available_evidence: List[str] = Field(
        default_factory=list,
        description="Evidence documents/facts that ARE present in the doc pack"
    )
    missing_evidence: List[str] = Field(
        default_factory=list,
        description="Evidence that is NOT present but required for approval"
    )
    rationale: str = Field(
        description="Explanation of evidence assessment"
    )
    citations: List[str] = Field(
        default_factory=list,
        description="List of excerpt IDs cited. ONLY cite provided excerpts."
    )


class FinalVerdict(BaseModel):
    """
    Output from the Judge Agent - the deterministic resolver.
    
    This agent applies explicit rules to resolve agent disagreements:
    1. Hard-stop violations → REJECT
    2. Missing critical evidence → INSUFFICIENT_EVIDENCE  
    3. Allowed + evidence sufficient + no veto → APPROVE
    """
    verdict: Literal["APPROVE", "REJECT", "INSUFFICIENT_EVIDENCE"] = Field(
        description="Final decision based on deterministic rules"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score (0-1) in the verdict"
    )
    violations: List[str] = Field(
        default_factory=list,
        description="Policy/contract violations found"
    )
    conditions_to_allow: List[str] = Field(
        default_factory=list,
        description="What must be done/provided to change the verdict to APPROVE"
    )
    citations: List[str] = Field(
        default_factory=list,
        description="All citations supporting the verdict. ONLY cite provided excerpts."
    )
    rule_applied: str = Field(
        description="Which deterministic rule fired (e.g., 'RULE_2: Evidence Missing')"
    )
