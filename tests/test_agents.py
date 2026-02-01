"""
Unit Tests for Agent Definitions

Tests for agent creation and prompt loading.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch

from src.agents.definitions import (
    create_policy_agent,
    create_risk_agent,
    create_evidence_agent,
    create_judge_agent,
    get_prompt_versions,
    _load_prompt,
    PROMPTS_DIR,
)
from src.schemas.agents import (
    PolicyAgentOutput,
    RiskAgentOutput,
    EvidenceAgentOutput,
    FinalVerdict,
)


class TestAgentCreation:
    """Tests for agent creation functions."""
    
    def test_create_policy_agent_name(self):
        """Test policy agent has correct name."""
        agent = create_policy_agent()
        assert agent.name == "PolicyAgent"
    
    def test_create_policy_agent_output_type(self):
        """Test policy agent has correct output type."""
        agent = create_policy_agent()
        assert agent.output_type == PolicyAgentOutput
    
    def test_create_risk_agent_name(self):
        """Test risk agent has correct name."""
        agent = create_risk_agent()
        assert agent.name == "RiskAgent"
    
    def test_create_risk_agent_output_type(self):
        """Test risk agent has correct output type."""
        agent = create_risk_agent()
        assert agent.output_type == RiskAgentOutput
    
    def test_create_evidence_agent_name(self):
        """Test evidence agent has correct name."""
        agent = create_evidence_agent()
        assert agent.name == "EvidenceAgent"
    
    def test_create_evidence_agent_output_type(self):
        """Test evidence agent has correct output type."""
        agent = create_evidence_agent()
        assert agent.output_type == EvidenceAgentOutput
    
    def test_create_judge_agent_name(self):
        """Test judge agent has correct name."""
        agent = create_judge_agent()
        assert agent.name == "JudgeAgent"
    
    def test_create_judge_agent_output_type(self):
        """Test judge agent has correct output type."""
        agent = create_judge_agent()
        assert agent.output_type == FinalVerdict


class TestAgentConfiguration:
    """Tests for agent configuration."""
    
    def test_custom_model_override(self):
        """Test that custom model can be passed."""
        agent = create_policy_agent(model="gpt-3.5-turbo")
        assert agent.model == "gpt-3.5-turbo"
    
    def test_default_model_used(self):
        """Test that default model is used when not specified."""
        agent = create_policy_agent()
        # Should use DEFAULT_MODEL or gpt-4o
        assert agent.model is not None
    
    def test_all_agents_have_instructions(self):
        """Test that all agents have instructions loaded."""
        policy = create_policy_agent()
        risk = create_risk_agent()
        evidence = create_evidence_agent()
        judge = create_judge_agent()
        
        assert policy.instructions is not None
        assert len(policy.instructions) > 0
        assert risk.instructions is not None
        assert len(risk.instructions) > 0
        assert evidence.instructions is not None
        assert len(evidence.instructions) > 0
        assert judge.instructions is not None
        assert len(judge.instructions) > 0


class TestPromptLoading:
    """Tests for prompt loading functionality."""
    
    def test_prompts_dir_exists(self):
        """Test that prompts directory exists."""
        assert PROMPTS_DIR.exists()
    
    def test_policy_prompt_exists(self):
        """Test that policy agent prompt file exists."""
        prompt_file = PROMPTS_DIR / "policy_agent_v1.txt"
        assert prompt_file.exists()
    
    def test_risk_prompt_exists(self):
        """Test that risk agent prompt file exists."""
        prompt_file = PROMPTS_DIR / "risk_agent_v1.txt"
        assert prompt_file.exists()
    
    def test_evidence_prompt_exists(self):
        """Test that evidence agent prompt file exists."""
        prompt_file = PROMPTS_DIR / "evidence_agent_v1.txt"
        assert prompt_file.exists()
    
    def test_judge_prompt_exists(self):
        """Test that judge agent prompt file exists."""
        prompt_file = PROMPTS_DIR / "judge_agent_v1.txt"
        assert prompt_file.exists()
    
    def test_load_prompt_returns_string(self):
        """Test that _load_prompt returns a string."""
        content = _load_prompt("policy_agent_v1.txt")
        assert isinstance(content, str)
        assert len(content) > 0
    
    def test_load_prompt_missing_raises(self):
        """Test that loading missing prompt raises error."""
        with pytest.raises(FileNotFoundError):
            _load_prompt("nonexistent_prompt.txt")


class TestPromptVersions:
    """Tests for prompt version tracking."""
    
    def test_get_prompt_versions_returns_dict(self):
        """Test that get_prompt_versions returns a dict."""
        versions = get_prompt_versions()
        assert isinstance(versions, dict)
    
    def test_get_prompt_versions_has_all_agents(self):
        """Test that versions include all agent types."""
        versions = get_prompt_versions()
        assert "policy" in versions
        assert "risk" in versions
        assert "evidence" in versions
        assert "judge" in versions
    
    def test_get_prompt_versions_values_are_strings(self):
        """Test that version values are strings."""
        versions = get_prompt_versions()
        for key, value in versions.items():
            assert isinstance(value, str)
    
    def test_get_prompt_versions_consistent(self):
        """Test that versions are consistent across calls."""
        versions1 = get_prompt_versions()
        versions2 = get_prompt_versions()
        assert versions1 == versions2
