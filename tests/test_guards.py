"""
Unit Tests for Citation Whitelist Guard

Tests for citation validation - ensuring zero hallucinations.
"""

import pytest

from src.guards.citation_whitelist import (
    validate_citations,
    validate_all_agent_outputs,
    get_all_citations_from_outputs,
    CitationValidationError,
)
from src.schemas.agents import (
    PolicyAgentOutput,
    RiskAgentOutput,
    EvidenceAgentOutput,
)


class TestValidateCitations:
    """Tests for validate_citations function."""
    
    def test_valid_citations_pass(self):
        """Test that valid citations pass validation."""
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="Policy allows this.",
            citations=["POL-001", "POL-002"]
        )
        
        allowed = {"POL-001", "POL-002", "POL-003", "CON-001"}
        is_valid, hallucinated = validate_citations(output, allowed)
        
        assert is_valid is True
        assert len(hallucinated) == 0
    
    def test_empty_citations_pass(self):
        """Test that empty citations pass validation."""
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="No citations needed.",
            citations=[]
        )
        
        allowed = {"POL-001"}
        is_valid, hallucinated = validate_citations(output, allowed)
        
        assert is_valid is True
        assert len(hallucinated) == 0
    
    def test_hallucinated_citations_detected(self):
        """Test that hallucinated citations are detected."""
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="Citing fake sources.",
            citations=["POL-001", "FAKE-001", "INVENTED-002"]
        )
        
        allowed = {"POL-001", "POL-002"}
        is_valid, hallucinated = validate_citations(output, allowed)
        
        assert is_valid is False
        assert len(hallucinated) == 2
        assert "FAKE-001" in hallucinated
        assert "INVENTED-002" in hallucinated
    
    def test_single_hallucinated_citation(self):
        """Test that even a single hallucinated citation fails."""
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="One bad citation.",
            citations=["POL-001", "POL-002", "NONEXISTENT-001"]
        )
        
        allowed = {"POL-001", "POL-002"}
        is_valid, hallucinated = validate_citations(output, allowed)
        
        assert is_valid is False
        assert hallucinated == ["NONEXISTENT-001"]
    
    def test_raise_on_error(self):
        """Test that raise_on_error raises exception."""
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="Bad citation.",
            citations=["FAKE-001"]
        )
        
        allowed = {"POL-001"}
        
        with pytest.raises(CitationValidationError) as exc_info:
            validate_citations(output, allowed, raise_on_error=True)
        
        assert "FAKE-001" in exc_info.value.hallucinated
        assert "POL-001" in exc_info.value.allowed
    
    def test_case_sensitive_citations(self):
        """Test that citation validation is case-sensitive."""
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="Case mismatch.",
            citations=["pol-001"]  # Lowercase
        )
        
        allowed = {"POL-001"}  # Uppercase
        is_valid, hallucinated = validate_citations(output, allowed)
        
        assert is_valid is False
        assert "pol-001" in hallucinated


class TestValidateAllAgentOutputs:
    """Tests for validating multiple agent outputs."""
    
    def test_all_agents_valid(self):
        """Test when all agents have valid citations."""
        outputs = {
            'policy': PolicyAgentOutput(
                stance="YES",
                conditions=[],
                rationale="Valid.",
                citations=["POL-001"]
            ),
            'risk': RiskAgentOutput(
                stance="YES",
                risk_flags=[],
                hard_stops=[],
                rationale="No risks.",
                citations=["CON-001"]
            ),
            'evidence': EvidenceAgentOutput(
                stance="SUFFICIENT",
                available_evidence=[],
                missing_evidence=[],
                rationale="All present.",
                citations=["EVI-001"]
            ),
        }
        
        allowed = {"POL-001", "CON-001", "EVI-001"}
        results = validate_all_agent_outputs(outputs, allowed)
        
        assert results['policy']['is_valid'] is True
        assert results['risk']['is_valid'] is True
        assert results['evidence']['is_valid'] is True
    
    def test_one_agent_invalid(self):
        """Test when one agent has hallucinated citations."""
        outputs = {
            'policy': PolicyAgentOutput(
                stance="YES",
                conditions=[],
                rationale="Valid.",
                citations=["POL-001"]
            ),
            'risk': RiskAgentOutput(
                stance="YES",
                risk_flags=[],
                hard_stops=[],
                rationale="Bad citation.",
                citations=["CON-001", "FAKE-001"]
            ),
        }
        
        allowed = {"POL-001", "CON-001", "EVI-001"}
        results = validate_all_agent_outputs(outputs, allowed)
        
        assert results['policy']['is_valid'] is True
        assert results['risk']['is_valid'] is False
        assert "FAKE-001" in results['risk']['hallucinated']


class TestGetAllCitationsFromOutputs:
    """Tests for extracting all citations from outputs."""
    
    def test_aggregate_citations(self):
        """Test that all citations are aggregated."""
        outputs = {
            'policy': PolicyAgentOutput(
                stance="YES",
                conditions=[],
                rationale="Test.",
                citations=["POL-001", "POL-002"]
            ),
            'risk': RiskAgentOutput(
                stance="YES",
                risk_flags=[],
                hard_stops=[],
                rationale="Test.",
                citations=["CON-001"]
            ),
        }
        
        all_citations = get_all_citations_from_outputs(outputs)
        
        assert len(all_citations) == 3
        assert "POL-001" in all_citations
        assert "POL-002" in all_citations
        assert "CON-001" in all_citations
    
    def test_duplicate_citations_deduplicated(self):
        """Test that duplicates are removed."""
        outputs = {
            'policy': PolicyAgentOutput(
                stance="YES",
                conditions=[],
                rationale="Test.",
                citations=["POL-001", "CON-001"]
            ),
            'risk': RiskAgentOutput(
                stance="YES",
                risk_flags=[],
                hard_stops=[],
                rationale="Test.",
                citations=["CON-001", "POL-001"]  # Duplicates
            ),
        }
        
        all_citations = get_all_citations_from_outputs(outputs)
        
        assert len(all_citations) == 2  # Deduplicated


class TestCitationValidationError:
    """Tests for CitationValidationError exception."""
    
    def test_error_message_format(self):
        """Test error message includes relevant info."""
        error = CitationValidationError(
            hallucinated=["FAKE-001", "FAKE-002"],
            allowed={"POL-001", "CON-001"}
        )
        
        message = str(error)
        assert "FAKE-001" in message
        assert "FAKE-002" in message
        assert "Hallucinated" in message
    
    def test_error_attributes(self):
        """Test error has correct attributes."""
        error = CitationValidationError(
            hallucinated=["FAKE-001"],
            allowed={"POL-001"}
        )
        
        assert error.hallucinated == ["FAKE-001"]
        assert error.allowed == {"POL-001"}
