"""
ProofGate Orchestrator

The heart of ProofGate - coordinates parallel agent execution
and deterministic verdict resolution.
"""

import asyncio
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from agents import Runner

from src.schemas.agents import (
    PolicyAgentOutput,
    RiskAgentOutput,
    EvidenceAgentOutput,
    FinalVerdict,
)
from src.schemas.documents import ExcerptBlock, RunTrace
from src.agents import (
    create_policy_agent,
    create_risk_agent,
    create_evidence_agent,
    create_judge_agent,
    get_prompt_versions,
)
from src.guards import validate_citations, CitationValidationError
from src.trace import TraceStore


class ProofGateOrchestrator:
    """
    Multi-agent orchestrator for financial compliance judgments.
    
    This is where multi-agent becomes necessary, not theatre:
    - Policy, Risk, Evidence run in PARALLEL (conflicting objectives)
    - Judge resolves conflicts with DETERMINISTIC rules
    - Guards enforce ZERO hallucinations
    """
    
    def __init__(
        self,
        data_dir: Path = None,
        deterministic_mode: bool = True,
        max_retries: int = 1,
    ):
        """
        Initialize orchestrator.
        
        Args:
            data_dir: Path to data directory
            deterministic_mode: If True, cache and replay identical inputs
            max_retries: Max retries on citation validation failure
        """
        self.data_dir = data_dir or Path("./data")
        self.deterministic_mode = deterministic_mode
        self.max_retries = max_retries
        
        # Create agents
        self.policy_agent = create_policy_agent()
        self.risk_agent = create_risk_agent()
        self.evidence_agent = create_evidence_agent()
        self.judge_agent = create_judge_agent()
        
        # Trace store
        self.trace_store = TraceStore(self.data_dir / "traces.db")
    
    async def init(self):
        """Initialize async components."""
        await self.trace_store.init_db()
    
    def _build_context(
        self,
        question: str,
        excerpts: Dict[str, List[ExcerptBlock]]
    ) -> str:
        """Build context string for agents."""
        context_parts = [
            f"## QUESTION\n{question}",
            "",
            "## POLICY_EXCERPTS",
        ]
        
        for excerpt in excerpts.get('policy', []):
            context_parts.append(f"{excerpt.cite_token}\n{excerpt.text}\n")
        
        context_parts.append("\n## CONTRACT_EXCERPTS")
        for excerpt in excerpts.get('contract', []):
            context_parts.append(f"{excerpt.cite_token}\n{excerpt.text}\n")
        
        context_parts.append("\n## EVIDENCE_EXCERPTS")
        for excerpt in excerpts.get('evidence', []):
            context_parts.append(f"{excerpt.cite_token}\n{excerpt.text}\n")
        
        return "\n".join(context_parts)
    
    def _build_judge_context(
        self,
        question: str,
        policy_output: PolicyAgentOutput,
        risk_output: RiskAgentOutput,
        evidence_output: EvidenceAgentOutput,
    ) -> str:
        """Build context for Judge agent with all agent outputs."""
        return f"""## QUESTION
{question}

## POLICY_AGENT_OUTPUT
Stance: {policy_output.stance}
Conditions: {policy_output.conditions}
Rationale: {policy_output.rationale}
Citations: {policy_output.citations}

## RISK_AGENT_OUTPUT
Stance: {risk_output.stance}
Risk Flags: {risk_output.risk_flags}
Hard Stops: {risk_output.hard_stops}
Rationale: {risk_output.rationale}
Citations: {risk_output.citations}

## EVIDENCE_AGENT_OUTPUT
Stance: {evidence_output.stance}
Available Evidence: {evidence_output.available_evidence}
Missing Evidence: {evidence_output.missing_evidence}
Rationale: {evidence_output.rationale}
Citations: {evidence_output.citations}
"""
    
    async def _run_agent_with_retry(
        self,
        agent,
        context: str,
        allowed_citations: set,
        agent_name: str,
    ):
        """Run an agent with citation validation and retry."""
        for attempt in range(self.max_retries + 1):
            result = await Runner.run(agent, input=context)
            output = result.final_output
            
            # Validate citations
            is_valid, hallucinated = validate_citations(
                output, allowed_citations
            )
            
            if is_valid:
                return output
            
            if attempt < self.max_retries:
                # Add correction to context and retry
                context += f"\n\nINVALID_CITATIONS: The following citations are not allowed: {hallucinated}. Allowed citations are: {sorted(allowed_citations)}. Please correct your response."
            else:
                # Final attempt failed - raise error or return with flag
                raise CitationValidationError(hallucinated, allowed_citations)
        
        return output
    
    async def run(
        self,
        question: str,
        excerpts: Dict[str, List[ExcerptBlock]],
    ) -> Dict[str, Any]:
        """
        Run the full ProofGate judgment pipeline.
        
        Args:
            question: The question to evaluate
            excerpts: Dict of excerpts by type
        
        Returns:
            Dict with verdict, agent_outputs, trace
        """
        start_time = time.time()
        run_id = str(uuid.uuid4())[:8]
        
        # Flatten excerpts and get allowed citations
        all_excerpts = [
            e for excerpt_list in excerpts.values() 
            for e in excerpt_list
        ]
        excerpt_ids = [e.excerpt_id for e in all_excerpts]
        allowed_citations = {e.excerpt_id for e in all_excerpts}
        prompt_versions = get_prompt_versions()
        
        # Compute input hash for caching
        input_hash = TraceStore.compute_input_hash(
            question, excerpt_ids, prompt_versions
        )
        
        # Check cache if deterministic mode
        if self.deterministic_mode:
            cached = await self.trace_store.get_cached_result(input_hash)
            if cached:
                # Return cached result with replayed flag
                cached['trace']['replayed'] = True
                return cached
        
        # Build context for parallel agents
        context = self._build_context(question, excerpts)
        
        # PARALLEL EXECUTION - The multi-agent magic
        # Three agents with conflicting objectives, running simultaneously
        try:
            policy_result, risk_result, evidence_result = await asyncio.gather(
                self._run_agent_with_retry(
                    self.policy_agent, context, allowed_citations, "policy"
                ),
                self._run_agent_with_retry(
                    self.risk_agent, context, allowed_citations, "risk"
                ),
                self._run_agent_with_retry(
                    self.evidence_agent, context, allowed_citations, "evidence"
                ),
            )
        except CitationValidationError as e:
            # Fail closed on citation validation error
            return self._fail_closed_result(
                run_id, question, excerpt_ids, prompt_versions,
                f"Citation validation failed: {e.hallucinated}"
            )
        except Exception as e:
            # Fail closed on any error
            return self._fail_closed_result(
                run_id, question, excerpt_ids, prompt_versions,
                f"Agent execution error: {str(e)}"
            )
        
        # JUDGE RESOLUTION - Deterministic rules
        judge_context = self._build_judge_context(
            question, policy_result, risk_result, evidence_result
        )
        
        try:
            judge_response = await Runner.run(
                self.judge_agent, input=judge_context
            )
            verdict = judge_response.final_output
        except Exception as e:
            return self._fail_closed_result(
                run_id, question, excerpt_ids, prompt_versions,
                f"Judge execution error: {str(e)}"
            )
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Build agent output hashes
        agent_output_hashes = {
            'policy': TraceStore.compute_output_hash(policy_result),
            'risk': TraceStore.compute_output_hash(risk_result),
            'evidence': TraceStore.compute_output_hash(evidence_result),
            'judge': TraceStore.compute_output_hash(verdict),
        }
        
        # Build trace
        trace = RunTrace(
            run_id=run_id,
            input_hash=input_hash,
            question=question,
            excerpt_ids=excerpt_ids,
            prompt_versions=prompt_versions,
            agent_output_hashes=agent_output_hashes,
            final_output_hash=agent_output_hashes['judge'],
            replayed=False,
            timestamp=datetime.utcnow().isoformat(),
            latency_ms=latency_ms,
        )
        
        # Build result
        result = {
            'run_id': run_id,
            'verdict': verdict.model_dump(),
            'agent_outputs': {
                'policy': policy_result.model_dump(),
                'risk': risk_result.model_dump(),
                'evidence': evidence_result.model_dump(),
            },
            'trace': trace.model_dump(),
            'excerpts_used': [e.model_dump() for e in all_excerpts],
        }
        
        # Store trace
        await self.trace_store.store_trace(trace, result)
        
        return result
    
    def _fail_closed_result(
        self,
        run_id: str,
        question: str,
        excerpt_ids: List[str],
        prompt_versions: Dict[str, str],
        error_message: str,
    ) -> Dict[str, Any]:
        """Return fail-closed result on error."""
        verdict = FinalVerdict(
            verdict="INSUFFICIENT_EVIDENCE",
            confidence=0.0,
            violations=[],
            conditions_to_allow=[f"SYSTEM_ERROR: {error_message}"],
            citations=[],
            rule_applied="FAIL_CLOSED_ON_ERROR",
        )
        
        trace = RunTrace(
            run_id=run_id,
            input_hash=TraceStore.compute_input_hash(
                question, excerpt_ids, prompt_versions
            ),
            question=question,
            excerpt_ids=excerpt_ids,
            prompt_versions=prompt_versions,
            agent_output_hashes={},
            final_output_hash=TraceStore.compute_output_hash(verdict),
            replayed=False,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        return {
            'run_id': run_id,
            'verdict': verdict.model_dump(),
            'agent_outputs': {},
            'trace': trace.model_dump(),
            'error': error_message,
        }
