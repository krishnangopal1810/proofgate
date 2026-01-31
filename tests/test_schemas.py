"""
Unit Tests for Schemas

Tests for Pydantic models used throughout ProofGate.
"""

import pytest
from pydantic import ValidationError

from src.schemas.agents import (
    PolicyAgentOutput,
    RiskAgentOutput,
    EvidenceAgentOutput,
    FinalVerdict,
)
from src.schemas.documents import (
    Document,
    ExcerptBlock,
    RunTrace,
)


class TestPolicyAgentOutput:
    """Tests for PolicyAgentOutput schema."""
    
    def test_valid_yes_stance(self):
        """Test YES stance with no conditions."""
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="Policy allows this action.",
            citations=["POL-001"]
        )
        assert output.stance == "YES"
        assert len(output.conditions) == 0
    
    def test_valid_yes_conditional_stance(self):
        """Test YES_CONDITIONAL with conditions."""
        output = PolicyAgentOutput(
            stance="YES_CONDITIONAL",
            conditions=["Customer acceptance required", "No disputes pending"],
            rationale="Policy permits if conditions met.",
            citations=["POL-001", "POL-002"]
        )
        assert output.stance == "YES_CONDITIONAL"
        assert len(output.conditions) == 2
    
    def test_invalid_stance_rejected(self):
        """Test that invalid stance values are rejected."""
        with pytest.raises(ValidationError):
            PolicyAgentOutput(
                stance="MAYBE",  # Invalid
                conditions=[],
                rationale="Test",
                citations=[]
            )
    
    def test_default_factory_for_lists(self):
        """Test that lists default to empty."""
        output = PolicyAgentOutput(
            stance="NO",
            rationale="Not allowed."
        )
        assert output.conditions == []
        assert output.citations == []


class TestRiskAgentOutput:
    """Tests for RiskAgentOutput schema."""
    
    def test_valid_with_hard_stops(self):
        """Test output with hard-stop violations."""
        output = RiskAgentOutput(
            stance="NO",
            risk_flags=["Prior revenue reversal"],
            hard_stops=["30-day termination window active"],
            rationale="Cannot approve due to hard-stop.",
            citations=["CON-007"]
        )
        assert output.stance == "NO"
        assert len(output.hard_stops) == 1
    
    def test_valid_with_risk_flags_only(self):
        """Test output with risk flags but no hard-stops."""
        output = RiskAgentOutput(
            stance="YES_CONDITIONAL",
            risk_flags=["Customer has disputed invoices before"],
            hard_stops=[],
            rationale="Risks exist but can proceed with caution.",
            citations=["CON-003"]
        )
        assert output.stance == "YES_CONDITIONAL"
        assert len(output.risk_flags) == 1
        assert len(output.hard_stops) == 0


class TestEvidenceAgentOutput:
    """Tests for EvidenceAgentOutput schema."""
    
    def test_sufficient_evidence(self):
        """Test SUFFICIENT stance."""
        output = EvidenceAgentOutput(
            stance="SUFFICIENT",
            available_evidence=["Signed acceptance", "Invoice"],
            missing_evidence=[],
            rationale="All required evidence present.",
            citations=["EVI-001", "EVI-002"]
        )
        assert output.stance == "SUFFICIENT"
        assert len(output.missing_evidence) == 0
    
    def test_missing_evidence(self):
        """Test MISSING stance with list of missing items."""
        output = EvidenceAgentOutput(
            stance="MISSING",
            available_evidence=["Invoice"],
            missing_evidence=["Customer acceptance", "Go-live confirmation"],
            rationale="Critical evidence not present.",
            citations=["EVI-001"]
        )
        assert output.stance == "MISSING"
        assert len(output.missing_evidence) == 2
    
    def test_partial_evidence(self):
        """Test PARTIAL stance."""
        output = EvidenceAgentOutput(
            stance="PARTIAL",
            available_evidence=["Invoice", "Project tracker"],
            missing_evidence=["Formal acceptance email"],
            rationale="Some evidence exists but key piece missing.",
            citations=["EVI-001", "EVI-002"]
        )
        assert output.stance == "PARTIAL"


class TestFinalVerdict:
    """Tests for FinalVerdict (Judge output) schema."""
    
    def test_approve_verdict(self):
        """Test APPROVE verdict."""
        verdict = FinalVerdict(
            verdict="APPROVE",
            confidence=0.85,
            violations=[],
            conditions_to_allow=[],
            citations=["POL-001", "CON-001"],
            rule_applied="RULE_5: All agents pass, approval granted"
        )
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence == 0.85
    
    def test_reject_verdict(self):
        """Test REJECT verdict."""
        verdict = FinalVerdict(
            verdict="REJECT",
            confidence=0.95,
            violations=["30-day termination clause violation"],
            conditions_to_allow=[],
            citations=["CON-007"],
            rule_applied="RULE_1: Hard-stop violation detected"
        )
        assert verdict.verdict == "REJECT"
        assert len(verdict.violations) == 1
    
    def test_insufficient_evidence_verdict(self):
        """Test INSUFFICIENT_EVIDENCE verdict."""
        verdict = FinalVerdict(
            verdict="INSUFFICIENT_EVIDENCE",
            confidence=0.3,
            violations=[],
            conditions_to_allow=["Attach signed acceptance email"],
            citations=["EVI-001"],
            rule_applied="RULE_2: Evidence Agent stance is MISSING"
        )
        assert verdict.verdict == "INSUFFICIENT_EVIDENCE"
        assert len(verdict.conditions_to_allow) == 1
    
    def test_confidence_bounds(self):
        """Test confidence must be 0-1."""
        with pytest.raises(ValidationError):
            FinalVerdict(
                verdict="APPROVE",
                confidence=1.5,  # Invalid - > 1
                violations=[],
                conditions_to_allow=[],
                citations=[],
                rule_applied="TEST"
            )
        
        with pytest.raises(ValidationError):
            FinalVerdict(
                verdict="APPROVE",
                confidence=-0.1,  # Invalid - < 0
                violations=[],
                conditions_to_allow=[],
                citations=[],
                rule_applied="TEST"
            )


class TestDocument:
    """Tests for Document schema."""
    
    def test_content_hash_auto_computed(self):
        """Test that content hash is automatically computed."""
        doc = Document(
            doc_id="test-doc",
            doc_type="policy",
            title="Test Document",
            content="This is test content."
        )
        # Hash should be computed
        assert doc.content_hash != ""
        assert len(doc.content_hash) == 64  # SHA256 hex digest
    
    def test_same_content_same_hash(self):
        """Test that same content produces same hash."""
        doc1 = Document(
            doc_id="doc-1",
            doc_type="policy",
            title="Doc 1",
            content="Same content"
        )
        doc2 = Document(
            doc_id="doc-2",
            doc_type="contract",
            title="Doc 2",
            content="Same content"
        )
        assert doc1.content_hash == doc2.content_hash


class TestExcerptBlock:
    """Tests for ExcerptBlock schema."""
    
    def test_create_factory(self):
        """Test the create factory method."""
        excerpt = ExcerptBlock.create(
            excerpt_id="POL-001",
            doc_id="policy_pack",
            doc_type="policy",
            text="Revenue recognition clause."
        )
        assert excerpt.excerpt_id == "POL-001"
        assert excerpt.cite_token == "[CITE=POL-001]"
        assert excerpt.doc_type == "policy"
    
    def test_cite_token_format(self):
        """Test cite token formatting."""
        excerpt = ExcerptBlock.create(
            excerpt_id="CON-007",
            doc_id="contract_k",
            doc_type="contract",
            text="Termination clause."
        )
        assert excerpt.cite_token == "[CITE=CON-007]"


class TestRunTrace:
    """Tests for RunTrace schema."""
    
    def test_compute_input_hash_deterministic(self):
        """Test that input hash is deterministic."""
        hash1 = RunTrace.compute_input_hash(
            question="Can we recognize revenue?",
            excerpt_ids=["POL-001", "CON-001"],
            prompt_versions={"policy": "v1", "risk": "v1"}
        )
        hash2 = RunTrace.compute_input_hash(
            question="Can we recognize revenue?",
            excerpt_ids=["POL-001", "CON-001"],
            prompt_versions={"policy": "v1", "risk": "v1"}
        )
        assert hash1 == hash2
    
    def test_input_hash_order_invariant(self):
        """Test that excerpt order doesn't affect hash."""
        hash1 = RunTrace.compute_input_hash(
            question="Test",
            excerpt_ids=["POL-001", "CON-001"],
            prompt_versions={"policy": "v1"}
        )
        hash2 = RunTrace.compute_input_hash(
            question="Test",
            excerpt_ids=["CON-001", "POL-001"],  # Different order
            prompt_versions={"policy": "v1"}
        )
        assert hash1 == hash2  # Should be same due to sorting
    
    def test_different_questions_different_hash(self):
        """Test that different questions produce different hashes."""
        hash1 = RunTrace.compute_input_hash(
            question="Question A",
            excerpt_ids=["POL-001"],
            prompt_versions={"policy": "v1"}
        )
        hash2 = RunTrace.compute_input_hash(
            question="Question B",
            excerpt_ids=["POL-001"],
            prompt_versions={"policy": "v1"}
        )
        assert hash1 != hash2
