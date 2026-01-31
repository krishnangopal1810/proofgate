"""
Golden Scenario Tests

These are the acceptance criteria tests from the PRD.
All must pass for the implementation to be complete.

NOTE: These tests require a valid OPENAI_API_KEY to run
against the actual OpenAI API. For unit testing without
API calls, see the mock tests.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from src.schemas.agents import (
    PolicyAgentOutput,
    RiskAgentOutput,
    EvidenceAgentOutput,
    FinalVerdict,
)
from src.schemas.documents import ExcerptBlock
from src.orchestrator import ProofGateOrchestrator
from src.ingest import load_all_documents
from src.retrieve import SimpleRetriever


# Skip tests if no API key (for CI without secrets)
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


class TestGoldenScenariosMocked:
    """
    Golden scenario tests with mocked LLM responses.
    These test the orchestration logic without actual API calls.
    """
    
    @pytest.fixture
    def mock_policy_output_conditional(self):
        """Mock policy output: YES_CONDITIONAL."""
        return PolicyAgentOutput(
            stance="YES_CONDITIONAL",
            conditions=["Customer acceptance must be documented"],
            rationale="Policy permits if acceptance is obtained.",
            citations=["POL-001", "POL-002"]
        )
    
    @pytest.fixture
    def mock_risk_output_with_flags(self):
        """Mock risk output with flags but no hard-stops."""
        return RiskAgentOutput(
            stance="YES_CONDITIONAL",
            risk_flags=["30-day termination window may be active"],
            hard_stops=[],
            rationale="Risks exist but no absolute blockers.",
            citations=["CON-007"]
        )
    
    @pytest.fixture
    def mock_evidence_missing(self):
        """Mock evidence output: MISSING."""
        return EvidenceAgentOutput(
            stance="MISSING",
            available_evidence=["Invoice dated 2026-01-15"],
            missing_evidence=["Signed customer acceptance"],
            rationale="Cannot verify acceptance without documentation.",
            citations=["EVI-001"]
        )
    
    @pytest.fixture
    def mock_evidence_sufficient(self):
        """Mock evidence output: SUFFICIENT."""
        return EvidenceAgentOutput(
            stance="SUFFICIENT",
            available_evidence=["Invoice", "Signed acceptance email"],
            missing_evidence=[],
            rationale="All required evidence is present.",
            citations=["EVI-001", "EVI-003"]
        )
    
    @pytest.fixture
    def mock_verdict_insufficient(self):
        """Mock verdict: INSUFFICIENT_EVIDENCE."""
        return FinalVerdict(
            verdict="INSUFFICIENT_EVIDENCE",
            confidence=0.3,
            violations=[],
            conditions_to_allow=["Attach signed customer acceptance"],
            citations=["POL-001", "EVI-001"],
            rule_applied="RULE_2: Evidence Agent stance is MISSING"
        )
    
    @pytest.fixture
    def mock_verdict_approve(self):
        """Mock verdict: APPROVE."""
        return FinalVerdict(
            verdict="APPROVE",
            confidence=0.85,
            violations=[],
            conditions_to_allow=[],
            citations=["POL-001", "CON-001", "EVI-001", "EVI-003"],
            rule_applied="RULE_5: All agents pass, approval granted"
        )
    
    @pytest.fixture
    def sample_excerpts(self):
        """Create sample excerpts for testing."""
        return {
            'policy': [
                ExcerptBlock.create(
                    "POL-001", "policy_pack", "policy",
                    "Revenue may be recognized when delivery is complete."
                ),
                ExcerptBlock.create(
                    "POL-002", "policy_pack", "policy",
                    "Customer acceptance must be documented."
                ),
            ],
            'contract': [
                ExcerptBlock.create(
                    "CON-001", "contract_k", "contract",
                    "Contract value: ₹12Cr."
                ),
                ExcerptBlock.create(
                    "CON-007", "contract_k", "contract",
                    "Customer may terminate within 30 days of go-live."
                ),
            ],
            'evidence': [
                ExcerptBlock.create(
                    "EVI-001", "evidence_invoice", "evidence",
                    "Invoice INV-2026-042 dated 2026-01-15."
                ),
            ],
        }
    
    @pytest.fixture
    def sample_excerpts_with_acceptance(self):
        """Sample excerpts including acceptance email."""
        return {
            'policy': [
                ExcerptBlock.create(
                    "POL-001", "policy_pack", "policy",
                    "Revenue may be recognized when delivery is complete."
                ),
                ExcerptBlock.create(
                    "POL-002", "policy_pack", "policy",
                    "Customer acceptance must be documented."
                ),
            ],
            'contract': [
                ExcerptBlock.create(
                    "CON-001", "contract_k", "contract",
                    "Contract value: ₹12Cr."
                ),
                ExcerptBlock.create(
                    "CON-007", "contract_k", "contract",
                    "Customer may terminate within 30 days of go-live."
                ),
            ],
            'evidence': [
                ExcerptBlock.create(
                    "EVI-001", "evidence_invoice", "evidence",
                    "Invoice INV-2026-042 dated 2026-01-15."
                ),
                ExcerptBlock.create(
                    "EVI-003", "evidence_acceptance", "evidence",
                    "Formal acceptance email from Rajesh Kumar."
                ),
            ],
        }
    
    @pytest.mark.asyncio
    async def test_scenario_a_missing_acceptance_verdict(
        self,
        sample_excerpts,
        mock_policy_output_conditional,
        mock_risk_output_with_flags,
        mock_evidence_missing,
        mock_verdict_insufficient,
    ):
        """
        Scenario A: Missing acceptance → INSUFFICIENT_EVIDENCE
        
        Given: Document pack WITHOUT acceptance email
        When: User asks about revenue recognition
        Then: Verdict should be INSUFFICIENT_EVIDENCE
        """
        # Create mock runner results
        mock_policy_result = MagicMock()
        mock_policy_result.final_output = mock_policy_output_conditional
        
        mock_risk_result = MagicMock()
        mock_risk_result.final_output = mock_risk_output_with_flags
        
        mock_evidence_result = MagicMock()
        mock_evidence_result.final_output = mock_evidence_missing
        
        mock_judge_result = MagicMock()
        mock_judge_result.final_output = mock_verdict_insufficient
        
        with patch('src.orchestrator.Runner') as MockRunner:
            # Setup mock to return different results based on call
            MockRunner.run = AsyncMock(side_effect=[
                mock_policy_result,
                mock_risk_result,
                mock_evidence_result,
                mock_judge_result,
            ])
            
            orchestrator = ProofGateOrchestrator()
            await orchestrator.init()
            
            result = await orchestrator.run(
                question="Can we recognize ₹12Cr revenue this quarter for Customer K?",
                excerpts=sample_excerpts,
            )
            
            # Assertions - Scenario A requirements
            assert result['verdict']['verdict'] == "INSUFFICIENT_EVIDENCE"
            assert "acceptance" in str(result['verdict']['conditions_to_allow']).lower()
            assert len(result['verdict']['citations']) > 0
    
    @pytest.mark.asyncio
    async def test_scenario_b_flip_to_approve(
        self,
        sample_excerpts,
        sample_excerpts_with_acceptance,
        mock_policy_output_conditional,
        mock_risk_output_with_flags,
        mock_evidence_missing,
        mock_evidence_sufficient,
        mock_verdict_insufficient,
        mock_verdict_approve,
    ):
        """
        Scenario B: Add acceptance → flips to APPROVE
        
        Given: First run without acceptance
        When: Acceptance email is added and re-run
        Then: Verdict should flip from INSUFFICIENT_EVIDENCE to APPROVE
        """
        # First run - without acceptance
        mock_policy_result = MagicMock()
        mock_policy_result.final_output = mock_policy_output_conditional
        
        mock_risk_result = MagicMock()
        mock_risk_result.final_output = mock_risk_output_with_flags
        
        mock_evidence_missing_result = MagicMock()
        mock_evidence_missing_result.final_output = mock_evidence_missing
        
        mock_verdict_insuff_result = MagicMock()
        mock_verdict_insuff_result.final_output = mock_verdict_insufficient
        
        # Second run - with acceptance
        mock_evidence_sufficient_result = MagicMock()
        mock_evidence_sufficient_result.final_output = mock_evidence_sufficient
        
        mock_verdict_approve_result = MagicMock()
        mock_verdict_approve_result.final_output = mock_verdict_approve
        
        with patch('src.orchestrator.Runner') as MockRunner:
            orchestrator = ProofGateOrchestrator(deterministic_mode=False)
            await orchestrator.init()
            
            # First run
            MockRunner.run = AsyncMock(side_effect=[
                mock_policy_result,
                mock_risk_result,
                mock_evidence_missing_result,
                mock_verdict_insuff_result,
            ])
            
            before = await orchestrator.run(
                question="Can we recognize ₹12Cr revenue this quarter for Customer K?",
                excerpts=sample_excerpts,
            )
            
            # Second run with acceptance
            MockRunner.run = AsyncMock(side_effect=[
                mock_policy_result,
                mock_risk_result,
                mock_evidence_sufficient_result,
                mock_verdict_approve_result,
            ])
            
            after = await orchestrator.run(
                question="Can we recognize ₹12Cr revenue this quarter for Customer K?",
                excerpts=sample_excerpts_with_acceptance,
            )
            
            # Assertions - Scenario B requirements
            assert before['verdict']['verdict'] == "INSUFFICIENT_EVIDENCE"
            assert after['verdict']['verdict'] == "APPROVE"
    
    @pytest.mark.asyncio
    async def test_scenario_c_hard_stop_reject(
        self,
        sample_excerpts,
        mock_policy_output_conditional,
    ):
        """
        Scenario C: Hard-stop violation → REJECT
        
        Given: Risk Agent identifies a hard-stop
        When: Judge evaluates
        Then: Verdict should be REJECT with violations listed
        """
        mock_policy_result = MagicMock()
        mock_policy_result.final_output = mock_policy_output_conditional
        
        # Risk with hard-stop
        mock_risk_output = RiskAgentOutput(
            stance="NO",
            risk_flags=["Prior revenue reversal"],
            hard_stops=["Active termination window - customer can cancel"],
            rationale="Hard-stop violation blocks approval.",
            citations=["CON-007"]
        )
        mock_risk_result = MagicMock()
        mock_risk_result.final_output = mock_risk_output
        
        mock_evidence_result = MagicMock()
        mock_evidence_result.final_output = EvidenceAgentOutput(
            stance="PARTIAL",
            available_evidence=["Invoice"],
            missing_evidence=["Full acceptance"],
            rationale="Some evidence present.",
            citations=["EVI-001"]
        )
        
        # Judge should REJECT due to hard-stop
        mock_verdict = FinalVerdict(
            verdict="REJECT",
            confidence=0.9,
            violations=["Active termination window"],
            conditions_to_allow=["Wait for 30-day window to expire"],
            citations=["CON-007"],
            rule_applied="RULE_1: Hard-stop violation detected"
        )
        mock_judge_result = MagicMock()
        mock_judge_result.final_output = mock_verdict
        
        with patch('src.orchestrator.Runner') as MockRunner:
            MockRunner.run = AsyncMock(side_effect=[
                mock_policy_result,
                mock_risk_result,
                mock_evidence_result,
                mock_judge_result,
            ])
            
            orchestrator = ProofGateOrchestrator()
            await orchestrator.init()
            
            result = await orchestrator.run(
                question="Can we recognize ₹12Cr revenue this quarter for Customer K?",
                excerpts=sample_excerpts,
            )
            
            # Assertions - Scenario C requirements
            assert result['verdict']['verdict'] == "REJECT"
            assert len(result['verdict']['violations']) > 0


class TestZeroHallucinations:
    """
    Tests ensuring zero hallucinated citations.
    This is a critical requirement from the PRD.
    """
    
    def test_citation_validation_catches_hallucinations(self):
        """Test that the guard catches any hallucinated citations."""
        from src.guards import validate_citations
        
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="Test",
            citations=["POL-001", "FAKE-999"]  # FAKE-999 is hallucinated
        )
        
        allowed = {"POL-001", "POL-002", "CON-001"}
        is_valid, hallucinated = validate_citations(output, allowed)
        
        assert is_valid is False
        assert "FAKE-999" in hallucinated
    
    def test_all_provided_citations_are_valid(self):
        """Test that only provided excerpt IDs are valid citations."""
        from src.guards import validate_citations
        
        output = PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="Test",
            citations=["POL-001", "CON-002", "EVI-001"]
        )
        
        allowed = {"POL-001", "POL-002", "CON-001", "CON-002", "EVI-001", "EVI-002"}
        is_valid, hallucinated = validate_citations(output, allowed)
        
        assert is_valid is True
        assert len(hallucinated) == 0
