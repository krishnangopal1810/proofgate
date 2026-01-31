"""
Agent Definitions

Create agents using OpenAI Agents SDK with structured outputs.
"""

import os
from pathlib import Path
from typing import Dict

from agents import Agent

from src.schemas.agents import (
    PolicyAgentOutput,
    RiskAgentOutput,
    EvidenceAgentOutput,
    FinalVerdict,
)


# Prompt directory
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

# Default model
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def _load_prompt(filename: str) -> str:
    """Load a prompt file from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding='utf-8')


def create_policy_agent(model: str = None) -> Agent:
    """
    Create the Policy Agent - the permissive interpreter.
    
    Finds ways to say YES while identifying conditions.
    """
    return Agent(
        name="PolicyAgent",
        instructions=_load_prompt("policy_agent_v1.txt"),
        output_type=PolicyAgentOutput,
        model=model or DEFAULT_MODEL,
    )


def create_risk_agent(model: str = None) -> Agent:
    """
    Create the Risk Agent - the conservative guardian.
    
    Finds audit landmines and hard-stop violations.
    """
    return Agent(
        name="RiskAgent",
        instructions=_load_prompt("risk_agent_v1.txt"),
        output_type=RiskAgentOutput,
        model=model or DEFAULT_MODEL,
    )


def create_evidence_agent(model: str = None) -> Agent:
    """
    Create the Evidence Agent - the strict verifier.
    
    Demands proof for every claim, fails closed on missing evidence.
    """
    return Agent(
        name="EvidenceAgent",
        instructions=_load_prompt("evidence_agent_v1.txt"),
        output_type=EvidenceAgentOutput,
        model=model or DEFAULT_MODEL,
    )


def create_judge_agent(model: str = None) -> Agent:
    """
    Create the Judge Agent - the deterministic resolver.
    
    Applies explicit rules to resolve agent disagreements.
    """
    return Agent(
        name="JudgeAgent",
        instructions=_load_prompt("judge_agent_v1.txt"),
        output_type=FinalVerdict,
        model=model or DEFAULT_MODEL,
    )


def get_prompt_versions() -> Dict[str, str]:
    """
    Get version info for all prompts.
    
    Used for trace hashing and reproducibility.
    """
    return {
        "policy": "v1",
        "risk": "v1",
        "evidence": "v1",
        "judge": "v1",
    }
