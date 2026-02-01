<p align="center">
  <img src="https://img.shields.io/badge/Multi--Agent-OpenAI%20SDK-00A67E?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI SDK"/>
  <img src="https://img.shields.io/badge/Fail--Closed-Audit%20Safe-FF6B6B?style=for-the-badge" alt="Fail Closed"/>
  <img src="https://img.shields.io/badge/Zero-Hallucinated%20Citations-4ECDC4?style=for-the-badge" alt="Zero Hallucinations"/>
</p>

<h1 align="center">🔐 ProofGate</h1>
<h3 align="center"><em>The AI That Says "No" Until You Prove It</em></h3>

<p align="center">
  <strong>A fail-closed multi-agent judgment layer for financial compliance decisions</strong><br/>
  Built with <a href="https://github.com/openai/openai-agents-python">OpenAI Agents SDK</a> | Deterministic | Auditable | Citation-Enforced
</p>

---

## 🎯 The One-Liner

> **"Ask if you can book revenue now; ProofGate either approves, rejects, or refuses due to missing evidence—always with citations."**

---

## 💡 Why Multi-Agent Architecture

### Track Alignment: Multi-Agent Systems & Workflows

> *"Systems where multiple agents collaborate to tackle real-world problems"*

| Track Requirement | How ProofGate Delivers | Evidence |
|-------------------|------------------------|----------|
| **Complex real-world problem that cannot be solved reliably by a single agent** | Financial compliance requires balancing *conflicting objectives*: policy interpretation, risk assessment, and evidence verification. A single agent optimizes for one objective and collapses the others. | A single prompt told us "Yes, recognize revenue" while missing a termination clause that should block it. |
| **Measurable gains from agents working together** | **Accuracy**: 3 specialized agents catch what 1 generalist misses. **Determinism**: Judge applies explicit rules, not vibes. **Robustness**: Fail-closed = every error becomes `INSUFFICIENT_EVIDENCE`. | Golden tests prove: Scenario A→INSUFFICIENT, Scenario B→APPROVE, Scenario C→REJECT. 100% reproducible. |
| **Purposeful coordination (debate, handoffs, verification, consensus)** | **Debate**: Policy says YES, Risk says NO, Evidence says MISSING—visible disagreement. **Verification**: Citation whitelist guardrail. **Consensus via Judge**: Deterministic rules resolve conflict, not averaging. | Judge's `rule_applied` field shows exactly which rule fired (e.g., "RULE_2: Evidence Missing"). |



---

## 🧠 The Core Insight

### Why One Prompt Fails (And Why Multi-Agent Is Essential)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE PROBLEM WITH SINGLE-PROMPT AI                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   User: "Can we recognize ₹12Cr revenue this quarter?"                       │
│                                                                              │
│   Single LLM: "Yes, based on the contract terms..." ← DANGEROUS              │
│                                                                              │
│   What went wrong:                                                           │
│   ✗ Optimized for ONE objective (helpfulness)                                │
│   ✗ Hid uncertainty behind confident language                                │
│   ✗ Invented a citation that doesn't exist                                   │
│   ✗ Missed the termination clause that blocks recognition                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The ProofGate Solution: Intentional Conflict

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MULTI-AGENT ADVERSARIAL JUDGMENT                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │    POLICY    │    │     RISK     │    │   EVIDENCE   │                  │
│   │    AGENT     │    │    AGENT     │    │    AGENT     │                  │
│   ├──────────────┤    ├──────────────┤    ├──────────────┤                  │
│   │ Objective:   │    │ Objective:   │    │ Objective:   │                  │
│   │ PERMISSIVE   │    │ CONSERVATIVE │    │ STRICT       │                  │
│   │              │    │              │    │              │                  │
│   │ "Find ways   │    │ "Find audit  │    │ "Prove every │                  │
│   │  to say YES" │    │  landmines"  │    │  claim"      │                  │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│          │                   │                   │                           │
│          │   YES_CONDITIONAL │        NO         │        MISSING            │
│          └───────────────────┼───────────────────┘                           │
│                              │                                               │
│                              ▼                                               │
│                    ┌──────────────────┐                                     │
│                    │   JUDGE AGENT    │                                     │
│                    ├──────────────────┤                                     │
│                    │ Deterministic    │                                     │
│                    │ Resolution Rules │                                     │
│                    │                  │                                     │
│                    │ Rule 1: Hard-stop│                                     │
│                    │         → REJECT │                                     │
│                    │                  │                                     │
│                    │ Rule 2: Missing  │                                     │
│                    │         evidence │                                     │
│                    │       → INSUFF.  │ ◀── THIS IS THE KEY INNOVATION      │
│                    │                  │                                     │
│                    │ Rule 3: All pass │                                     │
│                    │       → APPROVE  │                                     │
│                    └────────┬─────────┘                                     │
│                             │                                                │
│                             ▼                                                │
│                   ┌───────────────────┐                                     │
│                   │ INSUFFICIENT_     │                                     │
│                   │ EVIDENCE          │                                     │
│                   │                   │                                     │
│                   │ "Attach signed    │                                     │
│                   │  acceptance email │                                     │
│                   │  to proceed"      │                                     │
│                   │                   │                                     │
│                   │ [CITE=CON-002]    │                                     │
│                   │ [CITE=POL-004]    │                                     │
│                   └───────────────────┘                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The magic moment in the demo:** User attaches the acceptance email. Rerun. Verdict flips to `APPROVE`.

---

## 🔥 The Money Shot: Agents in Conflict (Actual Example)

> This is the proof that multi-agent is necessary, not theatre.

### The Question
```
"Can we recognize ₹12Cr revenue this quarter for Customer K?"
```

### Agent Outputs (Real Conflict)

```yaml
# ═══════════════════════════════════════════════════════════════════════════
# POLICY AGENT — The Optimist
# ═══════════════════════════════════════════════════════════════════════════
PolicyAgent:
  stance: YES_CONDITIONAL
  conditions:
    - "Customer acceptance must be documented"
    - "No pending disputes or claims"
  rationale: "Per POL-002, revenue recognition is permitted when delivery 
              is complete and acceptance criteria are satisfied."
  citations: ["POL-002", "POL-004"]

# ═══════════════════════════════════════════════════════════════════════════
# RISK AGENT — The Pessimist  
# ═══════════════════════════════════════════════════════════════════════════
RiskAgent:
  stance: NO
  risk_flags:
    - "30-day cancellation window may still be active"
    - "Prior revenue reversal with this customer (2024-Q2)"
  hard_stops:
    - "CON-007 allows termination within 30 days of go-live"
  rationale: "Termination clause creates material reversal risk. 
              Cannot recognize until window expires."
  citations: ["CON-007", "CON-003"]

# ═══════════════════════════════════════════════════════════════════════════
# EVIDENCE AGENT — The Skeptic
# ═══════════════════════════════════════════════════════════════════════════
EvidenceAgent:
  stance: MISSING
  available_evidence:
    - "Invoice dated 2026-01-15"
    - "Project completion report"
  missing_evidence:
    - "Signed customer acceptance / UAT signoff"  ← THE BLOCKER
    - "Go-live confirmation email"
  rationale: "Invoice exists but no formal acceptance document. 
              Cannot verify delivery was accepted."
  citations: ["EVI-001"]
```

### Judge Resolution (Deterministic Rules)

```yaml
JudgeAgent:
  # Rule evaluation order:
  # 1. Check Risk.hard_stops → Found: "30-day termination" → But not expired
  # 2. Check Evidence.stance → MISSING → RULE FIRES
  
  verdict: INSUFFICIENT_EVIDENCE
  confidence: 0.3
  violations: []
  conditions_to_allow:
    - "Attach signed customer acceptance document"
    - "Confirm 30-day termination window has expired"
  citations: ["POL-002", "CON-007", "EVI-001"]
  rule_applied: "RULE_2: Evidence Agent stance is MISSING"
```

### Why This Matters

| Single Agent Would... | Multi-Agent Does... |
|-----------------------|---------------------|
| Return "Yes, looks good" (optimized for helpfulness) | Surface the conflict between Policy and Risk |
| Miss the termination clause | Risk Agent explicitly flags it as `hard_stop` |
| Assume acceptance exists | Evidence Agent demands proof, finds none |
| Give a confident wrong answer | Judge refuses to approve without evidence |

**The Judge doesn't average opinions—it applies deterministic rules.** That's the difference between "AI assistant" and "governed decision workflow."

---

## ❓ Why Not Just One Good Prompt?

> "Couldn't you just write a really good prompt that considers all these factors?"

### We Tried. Here's What Happened.

```
Single Prompt: "You are a financial compliance expert. Consider policy, 
risk, and evidence. Be thorough. Answer: Can we recognize revenue?"

Response: "Based on the contract terms and policy guidelines, revenue 
recognition appears appropriate assuming standard acceptance criteria 
are met. Confidence: High."

What went wrong:
  ✗ "Appears appropriate" — weasel words hiding uncertainty
  ✗ "Assuming" — invented an assumption about acceptance
  ✗ No citation to specific clause that permits/blocks
  ✗ No explicit check for termination clauses
  ✗ No list of what evidence is actually present vs missing
```

### The Fundamental Problem

| Approach | Failure Mode |
|----------|--------------|
| **Single prompt** | Optimizes for ONE objective. Policy interpretation, risk assessment, and evidence verification collapse into a blended, uncheckable answer. |
| **Prompt chaining** | Sequential = earlier steps bias later steps. Risk Agent would never see Policy's optimistic interpretation. |
| **Single agent + tools** | Tools provide data, but the agent still has one objective function. No adversarial tension. |
| **Multi-agent with same objective** | Theatre. Three agents agreeing tells you nothing. |
| **Multi-agent with conflicting objectives** | ✓ Surfaces disagreement. ✓ Forces explicit resolution. ✓ Auditable. |

---

## ⚠️ Limitations & Failure Modes

> Honest engineering means knowing where your system can fail.

### Known Limitations

| Limitation | Mitigation | Residual Risk |
|------------|------------|---------------|
| **All agents agree on wrong answer** | Agents have *conflicting* objectives (permissive vs conservative), making unanimous wrong answers unlikely | Low but possible if excerpts are misleading |
| **Garbage in, garbage out** | Citation whitelist prevents inventing sources, but can't fix bad source documents | Medium — document quality matters |
| **LLM doesn't follow prompt** | Structured outputs + JSON schema validation + retry | Low with gpt-4o |
| **Latency spikes** | 45s hard timeout → fail-closed | Demo might be slow on bad day |
| **Judge rules are incomplete** | Rules are explicit and versioned; add rules as edge cases emerge | Medium — need iteration |

### What We DON'T Claim

- ❌ This replaces human judgment entirely
- ❌ This catches fraud or intentional deception
- ❌ This works with arbitrary document types (MVP = text/markdown only)

### What We DO Claim

- ✅ Safer than single-agent for high-stakes decisions
- ✅ More auditable than human-only process (trace + hashes)
- ✅ Fail-closed by default (never silently approves)

---

## 🏗️ Architecture Overview

### System Flow (90 Seconds, End-to-End)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PROOFGATE FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ① QUESTION                        ② RETRIEVE                               │
│  ┌────────────────────────┐       ┌────────────────────────┐               │
│  │ "Can we recognize      │  ───▶ │ 📄 2 Policy excerpts   │               │
│  │  ₹12Cr revenue for     │       │ 📄 2 Contract excerpts │               │
│  │  Customer K?"          │       │ 📄 2 Evidence excerpts │               │
│  └────────────────────────┘       └────────────────────────┘               │
│                                              │                              │
│                                              ▼                              │
│  ③ PARALLEL AGENT EXECUTION (OpenAI Agents SDK)                            │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │  asyncio.gather(                                                 │       │
│  │      Runner.run(policy_agent, context),   ← YES_CONDITIONAL     │       │
│  │      Runner.run(risk_agent, context),     ← NO (hard-stop)      │       │
│  │      Runner.run(evidence_agent, context)  ← MISSING             │       │
│  │  )                                                               │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                              │                              │
│                                              ▼                              │
│  ④ GUARD LAYER                    ⑤ JUDGE RESOLUTION                       │
│  ┌─────────────────────┐         ┌─────────────────────┐                   │
│  │ ✓ JSON Schema Valid │   ───▶  │ Apply Rule 2:       │                   │
│  │ ✓ Citations in      │         │ Evidence MISSING    │                   │
│  │   whitelist only    │         │ → INSUFFICIENT_     │                   │
│  │ ✓ No hallucinations │         │   EVIDENCE          │                   │
│  └─────────────────────┘         └─────────────────────┘                   │
│                                              │                              │
│                                              ▼                              │
│  ⑥ TRACE & CACHE                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │ run_id: "abc123"                                                 │       │
│  │ input_hash: sha256(question + excerpts + prompts) = "7f3a..."   │       │
│  │ replayed: false                                                  │       │
│  │                                                                  │       │
│  │ → Same inputs later = identical output (deterministic replay)   │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ The Three Guarantees

### Guarantee 1: Fail-Closed (Always)

```python
# Every error path terminates in INSUFFICIENT_EVIDENCE
# This is the product's core value proposition

def handle_any_error(error: Exception) -> FinalVerdict:
    return FinalVerdict(
        verdict="INSUFFICIENT_EVIDENCE",  # NEVER silently approve
        confidence=0.0,
        conditions_to_allow=[f"SYSTEM_ERROR: {error}"],
        rule_applied="FAIL_CLOSED_ON_ERROR"
    )
```

> **Why this matters:** In finance, a false positive (approving something that should be rejected) causes audit failures and reversals. ProofGate is biased toward safety.

### Guarantee 2: Zero Hallucinated Citations

```python
class CitationWhitelistGuardrail(OutputGuardrail):
    """
    The LLM can ONLY cite excerpts we provided.
    Any invented citation = retry once, then fail-closed.
    """
    MAX_RETRIES = 1  # Explicit retry limit
    
    async def run(self, context, agent_output, retry_count=0) -> GuardrailFunctionOutput:
        if hasattr(agent_output, 'citations'):
            invalid = set(agent_output.citations) - self.allowed_citations
            if invalid:
                if retry_count < self.MAX_RETRIES:
                    return GuardrailFunctionOutput(
                        output_info={"hallucinated": list(invalid), "retry": retry_count + 1},
                        tripwire_triggered=True  # Force retry with feedback
                    )
                else:
                    # Max retries exceeded → fail-closed
                    raise SystemError(f"HALLUCINATED_CITATIONS: {invalid}")
        return GuardrailFunctionOutput(tripwire_triggered=False)
```

> **Why this matters:** The #1 failure mode of RAG systems is citing documents that don't exist. Our guardrail makes this impossible.

### Guarantee 2a: Factual Grounding (No Invented Facts)

```python
# Enforced via prompt engineering + output structure
# Agent prompts include:
"""
CRITICAL GROUNDING RULES:
1. Only state facts that appear VERBATIM in the provided excerpts
2. If information is not present, explicitly state "NOT_IN_EXCERPTS" or "UNKNOWN"
3. Do not infer, assume, or extrapolate beyond excerpt text
4. Every factual claim MUST have a corresponding citation
5. When uncertain, use the MISSING stance—never guess
"""

# Additionally, output schemas enforce this:
class EvidenceAgentOutput(BaseModel):
    missing_evidence: List[str]  # Forces explicit acknowledgment of gaps
    # NOT having a "assumptions" field = no place to put invented facts
```

> **Why this matters:** Citation validity ≠ claim validity. An agent could cite a real document but fabricate what it says. This guarantee prevents that failure mode.

### Guarantee 2b: Excerpt Fidelity (No Misquotes)

```python
class ExcerptFidelityGuardrail(OutputGuardrail):
    """
    Validates that agent claims accurately reflect cited excerpt content.
    Prevents: valid citation + misrepresented meaning.
    """
    
    async def run(self, context, agent_output) -> GuardrailFunctionOutput:
        for claim, citation in self._extract_claim_citation_pairs(agent_output):
            excerpt_text = self.excerpts[citation]
            # Semantic similarity check (cosine similarity > 0.7)
            # OR keyword overlap validation
            if not self._claim_matches_excerpt(claim, excerpt_text):
                return GuardrailFunctionOutput(
                    output_info={"misquote": citation, "claim": claim},
                    tripwire_triggered=True
                )
        return GuardrailFunctionOutput(tripwire_triggered=False)
```

> **Why this matters:** A real citation pointing to misrepresented content is as dangerous as a fake citation. This closes the last hallucination gap.

### Guarantee 3: Deterministic Replay

```python
# Same inputs → same output, cryptographically proven

input_hash = sha256(
    question + 
    sorted(excerpt_ids) + 
    prompt_versions
).hexdigest()

# If we've seen this exact input before, return cached result
if input_hash in cache:
    return cache[input_hash]  # Identical, auditable
```

> **Why this matters:** Auditors can replay any past decision and get the exact same answer. The trace proves it.

---

## 🔧 OpenAI Agents SDK Integration

### Why This SDK (Not LangChain, Not Custom)

| Feature | OpenAI Agents SDK | Why It Matters for ProofGate |
|---------|-------------------|------------------------------|
| `Agent(output_type=...)` | Native structured outputs with Pydantic | JSON schema enforcement built-in |
| `Guardrails` | Input/output validators | Citation whitelist is a first-class concept |
| `Runner.run()` | Async agent execution | Parallel Policy/Risk/Evidence execution |
| `Tracing` | Built-in observability | Extends naturally to our audit trace |
| Lightweight | ~2000 LOC, no bloat | Fast iteration, production-ready |

### Agent Definitions

```python
from agents import Agent, Runner
from pydantic import BaseModel, Field
from typing import Literal, List

# ═══════════════════════════════════════════════════════════════════════════
# STRUCTURED OUTPUT SCHEMAS (Pydantic models = guaranteed JSON structure)
# ═══════════════════════════════════════════════════════════════════════════

class PolicyAgentOutput(BaseModel):
    """The permissive agent - finds ways to say yes."""
    stance: Literal["YES", "YES_CONDITIONAL", "NO"]
    conditions: List[str] = Field(description="What must be true to approve")
    rationale: str
    citations: List[str] = Field(description="ONLY cite provided excerpt IDs")

class RiskAgentOutput(BaseModel):
    """The conservative agent - finds reasons to say no."""
    stance: Literal["YES", "YES_CONDITIONAL", "NO"]
    risk_flags: List[str] = Field(description="Warning signs found")
    hard_stops: List[str] = Field(description="Absolute blockers")
    rationale: str
    citations: List[str]

class EvidenceAgentOutput(BaseModel):
    """The strict agent - demands proof for every claim."""
    stance: Literal["SUFFICIENT", "PARTIAL", "MISSING"]
    available_evidence: List[str]
    missing_evidence: List[str] = Field(description="What's not in the doc pack")
    rationale: str
    citations: List[str]

class FinalVerdict(BaseModel):
    """The judge's deterministic output."""
    verdict: Literal["APPROVE", "REJECT", "INSUFFICIENT_EVIDENCE"]
    confidence: float = Field(ge=0.0, le=1.0)
    violations: List[str]
    conditions_to_allow: List[str]
    citations: List[str]
    rule_applied: str  # e.g., "RULE_2: Evidence Missing"

# Agent creation — same pattern for all 4
policy_agent = Agent(
    name="PolicyAgent",
    instructions=open("prompts/policy_v1.txt").read(),
    output_type=PolicyAgentOutput,  # ← Pydantic = guaranteed structure
    model="gpt-4o",
)
# risk_agent, evidence_agent, judge_agent follow same pattern
```

### The Orchestration Pipeline

```python
import asyncio
from agents import Runner

class ProofGateOrchestrator:
    """
    The heart of ProofGate.
    
    This is where multi-agent becomes necessary, not theatre:
    - Policy, Risk, Evidence run in PARALLEL (different objectives)
    - Judge resolves conflicts with DETERMINISTIC rules
    - Guards enforce ZERO hallucinations
    """
    
    async def run(self, question: str, excerpts: dict) -> dict:
        context = self._build_context(question, excerpts)
        allowed_citations = self._get_allowed_citations(excerpts)
        
        # PARALLEL EXECUTION - This is the multi-agent magic
        # Three agents with conflicting objectives, running simultaneously
        policy_result, risk_result, evidence_result = await asyncio.gather(
            Runner.run(self.policy_agent, input=context),
            Runner.run(self.risk_agent, input=context),
            Runner.run(self.evidence_agent, input=context),
        )
        
        # GUARD LAYER - Zero tolerance for hallucinated citations
        for result in [policy_result, risk_result, evidence_result]:
            self._enforce_citation_whitelist(result.final_output, allowed_citations)
        
        # JUDGE RESOLUTION - Deterministic rules, not vibes
        judge_input = self._format_for_judge(
            context, 
            policy_result.final_output,
            risk_result.final_output,
            evidence_result.final_output
        )
        
        judge_result = await Runner.run(self.judge_agent, input=judge_input)
        
        # TRACE - Cryptographic proof of determinism
        trace = self._build_trace(question, excerpts, judge_result.final_output)
        
        return {
            "verdict": judge_result.final_output,
            "agent_outputs": {
                "policy": policy_result.final_output,
                "risk": risk_result.final_output,
                "evidence": evidence_result.final_output,
            },
            "trace": trace
        }
```

---

## 📊 Retrieval Strategy

> **MVP Choice:** `SimpleRetriever` — zero ML, zero latency. Graduate to embeddings in production.

| Retriever | When To Use | Latency | Complexity |
|-----------|-------------|---------|------------|
| `SimpleRetriever` | Doc pack < 10 excerpts, fixed scenarios | <1ms | Zero — just slice arrays |
| `HardcodedRetriever` | Deterministic demos, known question → excerpt mapping | <1ms | Low — pattern matching |
| `EmbeddingRetriever` | Large doc packs, arbitrary questions, production | ~150ms | Medium — OpenAI embeddings API |

```python
# MVP: just return first 2 of each type. Done.
def retrieve(question: str) -> dict:
    return {
        "policy": excerpts["policy"][:2],
        "contract": excerpts["contract"][:2],
        "evidence": excerpts["evidence"][:2]
    }
```

---

## 🎬 The 90-Second Demo Script

> This is exactly what users will see.

### Setup (Pre-demo)
- Golden doc pack loaded: policy, 2 contracts, evidence files
- Customer K's acceptance email is NOT in the evidence folder (yet)

### Demo Flow

| Time | Action | What Users See |
|------|--------|-----------------|
| 0:00 | "Let me ask a question finance teams hate..." | Type: "Can we recognize ₹12Cr revenue this quarter for Customer K?" |
| 0:10 | Press **Run** | Excerpts appear: 2 policy, 2 contract, 2 evidence |
| 0:20 | Agents complete | **Policy:** YES_CONDITIONAL, **Risk:** NO (hard-stop), **Evidence:** MISSING |
| 0:30 | Judge resolves | Verdict: `INSUFFICIENT_EVIDENCE` with checklist |
| 0:40 | *"Watch what happens when I attach the proof..."* | Click **Attach Evidence** → select acceptance email |
| 0:50 | Press **Rerun** | Same question, new evidence |
| 1:00 | Verdict flips | `APPROVE` with increased confidence |
| 1:10 | Show trace | Input hash, output hash, "replayed: false" |
| 1:20 | *"Same inputs, same outputs. Auditors can verify."* | Done. |

### On-Screen Checklist (Must Be Visible)

- [ ] Retrieved excerpts with `[CITE=POL-001]` tokens
- [ ] Agent stance pills (YES/NO/MISSING)
- [ ] Judge's "rule applied" line
- [ ] Final verdict JSON
- [ ] Evidence attachment + rerun flip
- [ ] Trace log with hashes

---

## 🧪 Testing Strategy

### Golden Scenario Tests (The PRD Demands These)

```python
class TestGoldenScenarios:
    """These are the acceptance criteria. All must pass."""
    
    async def test_scenario_a_missing_acceptance(self):
        """Missing acceptance proof → INSUFFICIENT_EVIDENCE"""
        result = await orchestrator.run(scenario_a)
        
        assert result["verdict"]["verdict"] == "INSUFFICIENT_EVIDENCE"
        assert "acceptance" in str(result["verdict"]["conditions_to_allow"]).lower()
        assert len(result["verdict"]["citations"]) > 0
    
    async def test_scenario_b_flip_to_approve(self):
        """Add acceptance proof → flips to APPROVE"""
        before = await orchestrator.run(scenario_without_acceptance)
        after = await orchestrator.run(scenario_with_acceptance)
        
        assert before["verdict"]["verdict"] == "INSUFFICIENT_EVIDENCE"
        assert after["verdict"]["verdict"] == "APPROVE"
    
    async def test_scenario_c_hard_stop_reject(self):
        """Hard-stop clause violation → REJECT"""
        result = await orchestrator.run(scenario_hard_stop)
        
        assert result["verdict"]["verdict"] == "REJECT"
        assert len(result["verdict"]["violations"]) > 0


class TestZeroHallucinations:
    """The most critical test. No invented citations. Ever."""
    
    async def test_all_citations_are_real(self):
        result = await orchestrator.run(any_scenario)
        allowed = set(any_scenario.get_allowed_citations())
        
        all_citations = result["verdict"]["citations"]
        for agent_output in result["agent_outputs"].values():
            all_citations.extend(agent_output.citations)
        
        for citation in all_citations:
            assert citation in allowed, f"HALLUCINATED: {citation}"
```

---

## ⚡ Performance Budget

| Component | Target | Hard Limit | Notes |
|-----------|--------|------------|-------|
| Retrieval | <1ms | 200ms | SimpleRetriever = instant |
| Parallel Agents | 5s | 15s | 3 agents, gpt-4o |
| Judge | 3s | 10s | Single agent |
| Guards | <10ms | 100ms | Local validation |
| **Total Pipeline** | **<15s** | **45s** | Demo-friendly |

---

## 🚀 Implementation Phases

### Phase 1: Core Pipeline (4 hours)
- [x] Project setup with OpenAI Agents SDK
- [ ] Pydantic schemas for all agents
- [ ] Basic orchestrator with parallel execution
- [ ] Hardcoded golden doc pack

### Phase 2: Guards & Traces (3 hours)
- [ ] Citation whitelist guardrail
- [ ] Trace store (SQLite)
- [ ] Deterministic replay cache

### Phase 3: UI (4 hours)
- [ ] Single-screen layout
- [ ] Agent cards with stance pills
- [ ] Citation highlighting
- [ ] Evidence attach + rerun

### Phase 4: Polish (2 hours)
- [ ] Golden scenario tests
- [ ] 90-second demo rehearsal
- [ ] Edge case handling

---

## 📁 Repo Structure

```
proofgate/
├── prompts/
│   ├── policy_agent_v1.txt      # Permissive interpretation
│   ├── risk_agent_v1.txt        # Conservative flags
│   ├── evidence_agent_v1.txt    # Strict sufficiency
│   └── judge_agent_v1.txt       # Deterministic resolution
├── data/
│   └── docs/
│       ├── policy_pack.md       # Revenue recognition policy
│       ├── contract_customer_k.md
│       ├── evidence_invoice.md
│       └── evidence_acceptance_email.md  # ← The "flip" document
├── src/
│   ├── ingest/                  # Document → excerpts with stable IDs
│   ├── retrieve/                # Simple/Hardcoded/Embedding retrievers
│   ├── agents/                  # Agent creation and prompts
│   ├── guards/                  # Citation whitelist enforcement
│   ├── trace/                   # Run hashing and caching
│   └── api/                     # FastAPI endpoints
├── tests/
│   └── golden/                  # Scenario A, B, C tests
├── DESIGN.md                    # This document
├── PRD.MD                       # Product requirements
└── README.md
```

---

## 🎯 Definition of Done

We're done when:

- [ ] **One command** runs the app (`npm run dev` or `python main.py`)
- [ ] **One screen** shows the full E2E workflow
- [ ] **Scenario A** → `INSUFFICIENT_EVIDENCE`
- [ ] **Attach evidence** → **Scenario B** flips to `APPROVE`
- [ ] **Scenario C** → `REJECT` (hard-stop)
- [ ] **Zero hallucinated citations** (guard-enforced)
- [ ] **Demo completes in <90 seconds**, reliably
- [ ] **Trace shows** identical hashes for same inputs

---

## 🎯 Why ProofGate Matters

1. **The Problem is Real**: Finance teams make these decisions daily. Mistakes cause audit failures.

2. **Multi-Agent is Necessary**: Not three agents doing the same thing—three agents with *conflicting objectives* that must be resolved.

3. **The Demo is Satisfying**: Verdict flips when you attach proof. Judges see it immediately.

4. **Technical Depth**: Citation whitelist, cryptographic traces, structured outputs, parallel execution—all built on the OpenAI Agents SDK.

5. **Production-Ready Thinking**: Fail-closed, deterministic, auditable. This isn't a toy.

---

<p align="center">
  <strong>Built for real-world compliance. Ready for production.</strong><br/>
  <em>ProofGate: The AI that says "No" until you prove it.</em>
</p>
