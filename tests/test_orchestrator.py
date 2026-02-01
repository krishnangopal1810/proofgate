"""
Unit Tests for ProofGate Orchestrator

Tests for the multi-agent orchestrator module.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

from src.orchestrator import ProofGateOrchestrator
from src.schemas.agents import (
    PolicyAgentOutput,
    RiskAgentOutput,
    EvidenceAgentOutput,
    FinalVerdict,
)
from src.schemas.documents import ExcerptBlock, RunTrace
from src.guards import CitationValidationError


class TestBuildContext:
    """Tests for context building methods."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance for testing."""
        return ProofGateOrchestrator(
            data_dir=Path("/tmp/test_proofgate"),
            deterministic_mode=False,
        )
    
    @pytest.fixture
    def sample_excerpts(self):
        """Sample excerpts for testing."""
        return {
            'policy': [
                ExcerptBlock.create("POL-001", "policy1", "policy", "Policy excerpt 1"),
                ExcerptBlock.create("POL-002", "policy1", "policy", "Policy excerpt 2"),
            ],
            'contract': [
                ExcerptBlock.create("CON-001", "contract1", "contract", "Contract excerpt 1"),
            ],
            'evidence': [
                ExcerptBlock.create("EVI-001", "evidence1", "evidence", "Evidence excerpt 1"),
            ],
        }
    
    def test_build_context_includes_question(self, orchestrator, sample_excerpts):
        """Test that context includes the question."""
        context = orchestrator._build_context("Test question?", sample_excerpts)
        
        assert "## QUESTION" in context
        assert "Test question?" in context
    
    def test_build_context_includes_all_excerpts(self, orchestrator, sample_excerpts):
        """Test that context includes all excerpt types."""
        context = orchestrator._build_context("Test?", sample_excerpts)
        
        assert "## POLICY_EXCERPTS" in context
        assert "[CITE=POL-001]" in context
        assert "[CITE=POL-002]" in context
        assert "## CONTRACT_EXCERPTS" in context
        assert "[CITE=CON-001]" in context
        assert "## EVIDENCE_EXCERPTS" in context
        assert "[CITE=EVI-001]" in context
    
    def test_build_context_empty_excerpts(self, orchestrator):
        """Test context building with empty excerpt categories."""
        empty_excerpts = {'policy': [], 'contract': [], 'evidence': []}
        context = orchestrator._build_context("Test?", empty_excerpts)
        
        # Should still have section headers
        assert "## POLICY_EXCERPTS" in context
        assert "## CONTRACT_EXCERPTS" in context
        assert "## EVIDENCE_EXCERPTS" in context


class TestBuildJudgeContext:
    """Tests for judge context building."""
    
    @pytest.fixture
    def orchestrator(self):
        return ProofGateOrchestrator(
            data_dir=Path("/tmp/test_proofgate"),
            deterministic_mode=False,
        )
    
    @pytest.fixture
    def agent_outputs(self):
        """Sample agent outputs."""
        return {
            'policy': PolicyAgentOutput(
                stance="YES_CONDITIONAL",
                conditions=["Acceptance required"],
                rationale="Policy permits with conditions.",
                citations=["POL-001"]
            ),
            'risk': RiskAgentOutput(
                stance="YES",
                risk_flags=["Minor risk"],
                hard_stops=[],
                rationale="Acceptable risk level.",
                citations=["CON-001"]
            ),
            'evidence': EvidenceAgentOutput(
                stance="SUFFICIENT",
                available_evidence=["Invoice", "Receipt"],
                missing_evidence=[],
                rationale="All evidence present.",
                citations=["EVI-001"]
            ),
        }
    
    def test_build_judge_context_includes_question(self, orchestrator, agent_outputs):
        """Test judge context includes the question."""
        context = orchestrator._build_judge_context(
            "Can we approve?",
            agent_outputs['policy'],
            agent_outputs['risk'],
            agent_outputs['evidence'],
        )
        
        assert "## QUESTION" in context
        assert "Can we approve?" in context
    
    def test_build_judge_context_includes_all_agents(self, orchestrator, agent_outputs):
        """Test judge context includes all agent outputs."""
        context = orchestrator._build_judge_context(
            "Test?",
            agent_outputs['policy'],
            agent_outputs['risk'],
            agent_outputs['evidence'],
        )
        
        assert "## POLICY_AGENT_OUTPUT" in context
        assert "YES_CONDITIONAL" in context
        assert "## RISK_AGENT_OUTPUT" in context
        assert "Minor risk" in context
        assert "## EVIDENCE_AGENT_OUTPUT" in context
        assert "SUFFICIENT" in context


class TestFailClosedResult:
    """Tests for fail-closed error handling."""
    
    @pytest.fixture
    def orchestrator(self):
        return ProofGateOrchestrator(
            data_dir=Path("/tmp/test_proofgate"),
            deterministic_mode=False,
        )
    
    def test_fail_closed_result_structure(self, orchestrator):
        """Test that fail-closed returns expected structure."""
        result = orchestrator._fail_closed_result(
            run_id="test-123",
            question="Test question?",
            excerpt_ids=["POL-001"],
            prompt_versions={"policy": "v1"},
            error_message="Test error",
        )
        
        assert 'run_id' in result
        assert 'verdict' in result
        assert 'agent_outputs' in result
        assert 'trace' in result
        assert 'error' in result
    
    def test_fail_closed_verdict_is_insufficient(self, orchestrator):
        """Test that fail-closed returns INSUFFICIENT_EVIDENCE verdict."""
        result = orchestrator._fail_closed_result(
            run_id="test-123",
            question="Test?",
            excerpt_ids=[],
            prompt_versions={},
            error_message="Error",
        )
        
        assert result['verdict']['verdict'] == "INSUFFICIENT_EVIDENCE"
        assert result['verdict']['confidence'] == 0.0
    
    def test_fail_closed_includes_error_message(self, orchestrator):
        """Test that fail-closed includes error in conditions."""
        result = orchestrator._fail_closed_result(
            run_id="test-123",
            question="Test?",
            excerpt_ids=[],
            prompt_versions={},
            error_message="Custom error message",
        )
        
        assert "Custom error message" in str(result['verdict']['conditions_to_allow'])
        assert result['error'] == "Custom error message"
    
    def test_fail_closed_has_trace(self, orchestrator):
        """Test that fail-closed result includes trace."""
        result = orchestrator._fail_closed_result(
            run_id="test-run",
            question="Test?",
            excerpt_ids=["POL-001"],
            prompt_versions={"policy": "v1"},
            error_message="Error",
        )
        
        assert result['trace']['run_id'] == "test-run"
        assert result['trace']['question'] == "Test?"
        assert "POL-001" in result['trace']['excerpt_ids']


class TestOrchestratorRunMocked:
    """Tests for orchestrator run method with mocked LLM calls."""
    
    @pytest.fixture
    def sample_excerpts(self):
        return {
            'policy': [
                ExcerptBlock.create("POL-001", "policy1", "policy", "Policy excerpt"),
            ],
            'contract': [
                ExcerptBlock.create("CON-001", "contract1", "contract", "Contract excerpt"),
            ],
            'evidence': [
                ExcerptBlock.create("EVI-001", "evidence1", "evidence", "Evidence excerpt"),
            ],
        }
    
    @pytest.fixture
    def mock_policy_output(self):
        return PolicyAgentOutput(
            stance="YES",
            conditions=[],
            rationale="Approved.",
            citations=["POL-001"]
        )
    
    @pytest.fixture
    def mock_risk_output(self):
        return RiskAgentOutput(
            stance="YES",
            risk_flags=[],
            hard_stops=[],
            rationale="No risks.",
            citations=["CON-001"]
        )
    
    @pytest.fixture
    def mock_evidence_output(self):
        return EvidenceAgentOutput(
            stance="SUFFICIENT",
            available_evidence=["Evidence"],
            missing_evidence=[],
            rationale="All present.",
            citations=["EVI-001"]
        )
    
    @pytest.fixture
    def mock_verdict(self):
        return FinalVerdict(
            verdict="APPROVE",
            confidence=0.9,
            violations=[],
            conditions_to_allow=[],
            citations=["POL-001", "CON-001", "EVI-001"],
            rule_applied="RULE_5"
        )
    
    @pytest.mark.asyncio
    async def test_run_returns_expected_keys(
        self,
        sample_excerpts,
        mock_policy_output,
        mock_risk_output,
        mock_evidence_output,
        mock_verdict,
    ):
        """Test that run returns all expected keys in result."""
        mock_policy_result = MagicMock()
        mock_policy_result.final_output = mock_policy_output
        
        mock_risk_result = MagicMock()
        mock_risk_result.final_output = mock_risk_output
        
        mock_evidence_result = MagicMock()
        mock_evidence_result.final_output = mock_evidence_output
        
        mock_judge_result = MagicMock()
        mock_judge_result.final_output = mock_verdict
        
        with patch('src.orchestrator.Runner') as MockRunner:
            MockRunner.run = AsyncMock(side_effect=[
                mock_policy_result,
                mock_risk_result,
                mock_evidence_result,
                mock_judge_result,
            ])
            
            orchestrator = ProofGateOrchestrator(deterministic_mode=False)
            await orchestrator.init()
            
            result = await orchestrator.run("Test question?", sample_excerpts)
            
            assert 'run_id' in result
            assert 'verdict' in result
            assert 'agent_outputs' in result
            assert 'trace' in result
            assert 'excerpts_used' in result
    
    @pytest.mark.asyncio
    async def test_run_agent_outputs_structure(
        self,
        sample_excerpts,
        mock_policy_output,
        mock_risk_output,
        mock_evidence_output,
        mock_verdict,
    ):
        """Test that agent outputs have correct structure."""
        mock_policy_result = MagicMock()
        mock_policy_result.final_output = mock_policy_output
        
        mock_risk_result = MagicMock()
        mock_risk_result.final_output = mock_risk_output
        
        mock_evidence_result = MagicMock()
        mock_evidence_result.final_output = mock_evidence_output
        
        mock_judge_result = MagicMock()
        mock_judge_result.final_output = mock_verdict
        
        with patch('src.orchestrator.Runner') as MockRunner:
            MockRunner.run = AsyncMock(side_effect=[
                mock_policy_result,
                mock_risk_result,
                mock_evidence_result,
                mock_judge_result,
            ])
            
            orchestrator = ProofGateOrchestrator(deterministic_mode=False)
            await orchestrator.init()
            
            result = await orchestrator.run("Test?", sample_excerpts)
            
            assert 'policy' in result['agent_outputs']
            assert 'risk' in result['agent_outputs']
            assert 'evidence' in result['agent_outputs']
    
    @pytest.mark.asyncio
    async def test_run_trace_has_required_fields(
        self,
        sample_excerpts,
        mock_policy_output,
        mock_risk_output,
        mock_evidence_output,
        mock_verdict,
    ):
        """Test that trace includes required fields."""
        mock_policy_result = MagicMock()
        mock_policy_result.final_output = mock_policy_output
        
        mock_risk_result = MagicMock()
        mock_risk_result.final_output = mock_risk_output
        
        mock_evidence_result = MagicMock()
        mock_evidence_result.final_output = mock_evidence_output
        
        mock_judge_result = MagicMock()
        mock_judge_result.final_output = mock_verdict
        
        with patch('src.orchestrator.Runner') as MockRunner:
            MockRunner.run = AsyncMock(side_effect=[
                mock_policy_result,
                mock_risk_result,
                mock_evidence_result,
                mock_judge_result,
            ])
            
            orchestrator = ProofGateOrchestrator(deterministic_mode=False)
            await orchestrator.init()
            
            result = await orchestrator.run("Test?", sample_excerpts)
            
            trace = result['trace']
            assert 'run_id' in trace
            assert 'input_hash' in trace
            assert 'question' in trace
            assert 'excerpt_ids' in trace
            assert 'prompt_versions' in trace


class TestOrchestratorErrorHandling:
    """Tests for orchestrator error handling."""
    
    @pytest.fixture
    def sample_excerpts(self):
        return {
            'policy': [
                ExcerptBlock.create("POL-001", "policy1", "policy", "Policy"),
            ],
            'contract': [],
            'evidence': [],
        }
    
    @pytest.mark.asyncio
    async def test_citation_error_fails_closed(self, sample_excerpts):
        """Test that citation validation error results in fail-closed."""
        with patch('src.orchestrator.Runner') as MockRunner:
            # Make runner raise citation validation error
            MockRunner.run = AsyncMock(side_effect=CitationValidationError(
                hallucinated=["FAKE-001"],
                allowed={"POL-001"}
            ))
            
            orchestrator = ProofGateOrchestrator(deterministic_mode=False, max_retries=0)
            await orchestrator.init()
            
            result = await orchestrator.run("Test?", sample_excerpts)
            
            assert result['verdict']['verdict'] == "INSUFFICIENT_EVIDENCE"
            assert "Citation validation" in result['error']
    
    @pytest.mark.asyncio
    async def test_agent_exception_fails_closed(self, sample_excerpts):
        """Test that agent execution error results in fail-closed."""
        with patch('src.orchestrator.Runner') as MockRunner:
            MockRunner.run = AsyncMock(side_effect=Exception("API error"))
            
            orchestrator = ProofGateOrchestrator(deterministic_mode=False)
            await orchestrator.init()
            
            result = await orchestrator.run("Test?", sample_excerpts)
            
            assert result['verdict']['verdict'] == "INSUFFICIENT_EVIDENCE"
            assert "error" in result['error'].lower()
