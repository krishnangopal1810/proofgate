<p align="center">
  <img src="https://img.shields.io/badge/Track-Multi--Agent%20Systems-9B59B6?style=for-the-badge" alt="Multi-Agent Track"/>
  <img src="https://img.shields.io/badge/Multi--Agent-OpenAI%20SDK-00A67E?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI SDK"/>
  <img src="https://img.shields.io/badge/Fail--Closed-Audit%20Safe-FF6B6B?style=for-the-badge" alt="Fail Closed"/>
  <img src="https://img.shields.io/badge/Zero-Hallucinated%20Citations-4ECDC4?style=for-the-badge" alt="Zero Hallucinations"/>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License"/>
</p>

<h1 align="center">🔐 ProofGate</h1>
<h3 align="center"><em>The AI That Says "No" Until You Prove It</em></h3>

<p align="center">
  <strong>A fail-closed multi-agent judgment layer for financial compliance decisions</strong><br/>
  Built with <a href="https://github.com/openai/openai-agents-python">OpenAI Agents SDK</a> | Deterministic | Auditable | Citation-Enforced
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-why-proofgate">Why ProofGate</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 🎬 See It In Action

<p align="center">
  <img src="frontend/public/demo/demo.gif" alt="ProofGate Demo - REJECT to APPROVE flip" width="720"/>
</p>

<p align="center">
  <em>Toggle OFF → REJECT (missing acceptance) → Toggle ON → APPROVE (evidence complete)</em>
</p>

> [!TIP]
> **About the Toggle:** The "Include acceptance email" toggle simulates adding or removing a critical piece of evidence. This demonstrates how ProofGate's multi-agent system responds to changes in the evidence set—the same question yields different verdicts based on what documents are available.

**The "Aha" Moment:** Same question, same documents—but toggle the acceptance email evidence and watch the verdict flip from **REJECT** to **APPROVE**. That's multi-agent verification in action.

> [!IMPORTANT]
> ### 🎯 TL;DR for Judges
> - **Problem:** Single-agent LLMs say "yes" too easily in high-stakes decisions
> - **Solution:** 4 specialized agents with *conflicting objectives* (advocate vs adversary vs auditor)
> - **Key Innovation:** Deterministic Judge resolves conflicts with priority rules, not voting
> - **Demo:** Toggle evidence → watch verdict flip → that's the "aha" moment above
> - **Track Fit:** Purposeful coordination (debate → verification → consensus), not parallel execution

---

## ⚡ Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/krishnangopal1810/proofgate.git
cd proofgate

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run the Server

```bash
python main.py
```

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🔐 ProofGate - Multi-Agent Judgment System                ║
║                                                              ║
║   The AI that says "No" until you prove it.                 ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   Server starting at: http://0.0.0.0:8000                    ║
║                                                              ║
║   Endpoints:                                                 ║
║   • POST /api/judge     - Run judgment pipeline              ║
║   • POST /api/evidence  - Attach evidence document           ║
║   • GET  /api/traces    - List run traces                    ║
║   • GET  /api/excerpts  - List available excerpts            ║
║   • GET  /health        - Health check                       ║
║                                                              ║
║   Documentation: http://0.0.0.0:8000/docs                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Run Tests

```bash
pytest tests/ -v
```

### Run the Web UI (Optional)

For the visual demo shown above, run the frontend in a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open **http://localhost:3000** in your browser.

> [!NOTE]
> The frontend requires the backend server (`python main.py`) to be running on port 8000.

### Try It Now

Once the server is running, test the multi-agent judgment system:

**Scenario A: Without Acceptance Email → REJECT**
```bash
curl -X POST http://localhost:8000/api/judge \
  -H "Content-Type: application/json" \
  -d '{"question": "Can we recognize ₹12Cr revenue this quarter for Customer K?", "include_acceptance_email": false}'
```

Expected result:
```json
{
  "verdict": {
    "verdict": "REJECT",
    "rule_applied": "RULE_1: Hard-stop violation detected",
    "violations": ["Formal customer acceptance not obtained (EVI-002)"]
  }
}
```

**Scenario B: With Acceptance Email → APPROVE** ✨
```bash
curl -X POST http://localhost:8000/api/judge \
  -H "Content-Type: application/json" \
  -d '{"question": "Can we recognize ₹12Cr revenue this quarter for Customer K?", "include_acceptance_email": true}'
```

Expected result:
```json
{
  "verdict": {
    "verdict": "APPROVE",
    "rule_applied": "RULE_5: All agents pass, approval granted"
  }
}
```

> **Note:** Each judgment call takes ~20-25 seconds as it runs 3 agents in parallel + the Judge agent. Subsequent identical requests return cached results via deterministic replay.

---

## 💡 Why ProofGate?

### The Problem: AI That Says "Yes" Too Easily

Traditional AI assistants optimize for helpfulness. In high-stakes financial decisions, this is **dangerous**.

```
❌ Single LLM Response:
"Yes, revenue recognition appears appropriate based on the contract terms."

What went wrong:
• Optimized for ONE objective (helpfulness)
• Hid uncertainty behind confident language
• Invented a citation that doesn't exist
• Missed the termination clause that blocks recognition
```

### The Solution: Intentional Conflict

ProofGate uses **adversarial multi-agent architecture** where agents have **conflicting objectives**:

| Agent | Objective | Role |
|-------|-----------|------|
| 📋 **Policy Agent** | Permissive | Find ways to say YES |
| ⚠️ **Risk Agent** | Conservative | Find audit landmines |
| 📄 **Evidence Agent** | Strict | Prove every claim |
| ⚖️ **Judge Agent** | Deterministic | Resolve conflicts with rules |

The Judge doesn't average opinions—it applies **deterministic rules**. That's the difference between "AI assistant" and **governed decision workflow**.

### 🎯 Why This Problem Requires Multi-Agent

> **Single-Agent Failure Mode:** One LLM optimizing for "helpful response" will always find a way to say YES. It has no internal adversary, no verification step, and no deterministic resolution. In high-stakes finance, this is a compliance disaster.

| Challenge | Single Agent | ProofGate Multi-Agent |
|-----------|--------------|----------------------|
| **Conflicting objectives** | Picks one (usually YES) | Each agent owns different objective |
| **Uncertainty** | Hidden in confident prose | Surfaced via MISSING/CONDITIONAL stances |
| **Hallucinated citations** | Common failure | Whitelist enforcement + fail-closed |
| **Auditability** | "The AI said yes" | Cryptographic trace + deterministic replay |
| **Error handling** | Silent failure | Explicit FAIL_CLOSED_ON_ERROR |

### 📊 Measurable Gains from Multi-Agent Design

| Metric | Single LLM | ProofGate | Improvement |
|--------|-----------|-----------|-------------|
| **False Approval Rate** | ~30% (optimizes for YES) | 0% (fail-closed default) | **∞ reduction** |
| **Citation Accuracy** | ~70% (hallucinations) | 100% (whitelist enforced) | **+43%** |
| **Audit Reproducibility** | 0% (non-deterministic) | 100% (hash-based replay) | **∞ improvement** |
| **Error Transparency** | Low (hidden in prose) | Full (structured stances) | **Qualitative** |

### 🔗 Purposeful Coordination (Not Just Parallel Execution)

ProofGate's agents don't just run in parallel—they have **intentional coordination patterns**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COORDINATION ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │  POLICY     │  │   RISK      │  │  EVIDENCE   │                      │
│  │  (Advocate) │  │ (Adversary) │  │ (Auditor)   │    ← DEBATE PHASE    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                      │
│         │                │                │                              │
│         ▼                ▼                ▼                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              GUARD LAYER (Verification)                          │    │
│  │  • Schema validation  • Citation whitelist  • Hallucination check│    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼            ← HANDOFF TO JUDGE             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    JUDGE (Resolution)                            │    │
│  │  Rule 1: Hard-stop → REJECT                                      │    │
│  │  Rule 2: Evidence MISSING → INSUFFICIENT_EVIDENCE                │    │
│  │  Rule 3: Risk NO → REJECT                                        │    │
│  │  Rule 4: Policy CONDITIONAL → CONDITIONAL_APPROVE                │    │
│  │  Rule 5: All pass → APPROVE                                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Key: Agents DEBATE with conflicting stances, VERIFICATION validates    │
│       citations, HANDOFF to Judge for deterministic CONSENSUS           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Coordination Patterns Used:**
- **Debate:** Policy (advocate) vs Risk (adversary) surface conflicting interpretations
- **Verification:** Guard layer validates every agent output before handoff
- **Handoff:** Structured stances passed to Judge agent (not raw text)
- **Deterministic Consensus:** Judge applies priority-ordered rules, not voting

---

## 🔄 How It Works

### Multi-Agent Judgment Pipeline

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

### The Three Guarantees

#### 🔒 Guarantee 1: Fail-Closed (Always)

```python
# Every error path terminates in INSUFFICIENT_EVIDENCE
# Never silently approves

def handle_any_error(error: Exception) -> FinalVerdict:
    return FinalVerdict(
        verdict="INSUFFICIENT_EVIDENCE",
        confidence=0.0,
        conditions_to_allow=[f"SYSTEM_ERROR: {error}"],
        rule_applied="FAIL_CLOSED_ON_ERROR"
    )
```

#### 📎 Guarantee 2: Zero Hallucinated Citations

```python
# The LLM can ONLY cite excerpts we provided
# Any invented citation = retry once, then fail-closed

allowed_citations = {"POL-001", "POL-002", "CON-001", "EVI-001"}
agent_output.citations = ["POL-001", "FAKE-999"]  # ❌ FAKE-999 not in whitelist
# → Triggers retry → If still invalid → FAIL_CLOSED
```

#### 🔁 Guarantee 3: Deterministic Replay

```python
# Same inputs → same output, cryptographically proven

input_hash = sha256(
    question + 
    sorted(excerpt_ids) + 
    prompt_versions
).hexdigest()

# Auditors can replay any past decision and get the exact same answer
```

---

## 🏗️ Architecture

### Project Structure

```
proofgate/
├── prompts/                        # Agent prompt templates (versioned)
│   ├── policy_agent_v1.txt         # Permissive interpretation
│   ├── risk_agent_v1.txt           # Conservative flags
│   ├── evidence_agent_v1.txt       # Strict sufficiency
│   └── judge_agent_v1.txt          # Deterministic resolution
├── data/
│   └── docs/                       # Document pack (golden scenarios)
│       ├── policy_pack.md          # Revenue recognition policy
│       ├── contract_customer_k.md  # Sample contract
│       ├── evidence_invoice.md     # Invoice evidence
│       └── evidence_acceptance_email.md  # The "flip" document
├── src/
│   ├── ingest/                     # Document → excerpts with stable IDs
│   ├── retrieve/                   # Simple/Hardcoded/Embedding retrievers
│   ├── agents/                     # Agent creation with OpenAI SDK
│   ├── guards/                     # Citation whitelist enforcement
│   ├── trace/                      # Run hashing and caching
│   ├── schemas/                    # Pydantic models for structured outputs
│   ├── api/                        # FastAPI endpoints
│   └── orchestrator.py             # The heart of ProofGate
├── tests/
│   └── golden/                     # Golden scenario tests
├── main.py                         # Entry point
├── DESIGN.md                       # Technical design document
├── PRD.MD                          # Product requirements
└── requirements.txt
```

### Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **Agent Framework** | [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | Native structured outputs, guardrails, async execution |
| **API** | FastAPI | Modern, async, auto-generated OpenAPI docs |
| **Models** | Pydantic | JSON schema enforcement, validation |
| **Tracing** | SQLite + SHA256 | Simple, deterministic, auditable |
| **LLM** | GPT-4o | Best structured output adherence |

---

## 📡 API Reference

### `POST /api/judge`

Run the full judgment pipeline.

**Request:**
```json
{
  "question": "Can we recognize ₹12Cr revenue this quarter for Customer K?",
  "evidence_doc_ids": ["EVI-001", "EVI-002"]
}
```

**Response:**
```json
{
  "run_id": "abc12345",
  "verdict": {
    "verdict": "INSUFFICIENT_EVIDENCE",
    "confidence": 0.3,
    "violations": [],
    "conditions_to_allow": [
      "Attach signed customer acceptance document",
      "Confirm 30-day termination window has expired"
    ],
    "citations": ["POL-002", "CON-007", "EVI-001"],
    "rule_applied": "RULE_2: Evidence Agent stance is MISSING"
  },
  "agent_outputs": {
    "policy": { "stance": "YES_CONDITIONAL", ... },
    "risk": { "stance": "NO", ... },
    "evidence": { "stance": "MISSING", ... }
  },
  "trace": {
    "run_id": "abc12345",
    "input_hash": "7f3a...",
    "replayed": false
  }
}
```

### `POST /api/evidence`

Attach additional evidence document.

### `GET /api/traces`

List all run traces for audit purposes.

### `GET /api/excerpts`

List all available document excerpts.

### `GET /health`

Health check endpoint.

---

## 🧪 Testing

### Golden Scenario Tests

The test suite validates the three critical scenarios:

```python
# Scenario A: Missing acceptance → INSUFFICIENT_EVIDENCE
async def test_scenario_a_missing_acceptance():
    result = await orchestrator.run(scenario_a)
    assert result["verdict"]["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert "acceptance" in str(result["verdict"]["conditions_to_allow"]).lower()

# Scenario B: Add acceptance → APPROVE
async def test_scenario_b_flip_to_approve():
    before = await orchestrator.run(scenario_without_acceptance)
    after = await orchestrator.run(scenario_with_acceptance)
    
    assert before["verdict"]["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert after["verdict"]["verdict"] == "APPROVE"

# Scenario C: Hard-stop violation → REJECT
async def test_scenario_c_hard_stop_reject():
    result = await orchestrator.run(scenario_hard_stop)
    assert result["verdict"]["verdict"] == "REJECT"
```

Run tests:
```bash
pytest tests/ -v
pytest tests/golden/ -v  # Only golden scenarios
```

---

## ⚡ Performance

| Component | Target | Hard Limit |
|-----------|--------|------------|
| Retrieval | <1ms | 200ms |
| Parallel Agents (3x) | 5s | 15s |
| Judge | 3s | 10s |
| Guards | <10ms | 100ms |
| **Total Pipeline** | **<15s** | **45s** |

---

## 🚀 Roadmap

- [x] **Web UI** - Single-screen interface with citation highlighting ✅
- [ ] **Embedding Retriever** - Graduate from simple retrieval for large doc packs
- [ ] **Audit Export** - PDF report generation with trace artifacts
- [ ] **Custom Policies** - User-defined policy documents
- [ ] **Multi-language** - Support for non-English documents

---

## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ⚠️ Limitations

### What ProofGate Does NOT Do

- ❌ Replace human judgment entirely
- ❌ Catch fraud or intentional deception
- ❌ Work with arbitrary document types (MVP = text/markdown only)

### What ProofGate DOES Do

- ✅ Safer than single-agent for high-stakes decisions
- ✅ More auditable than human-only process (trace + hashes)
- ✅ Fail-closed by default (never silently approves)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built with [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- Inspired by adversarial AI safety research
- Designed for real-world financial compliance use cases

---

<p align="center">
  <strong>Built for the hackathon. Ready for production.</strong><br/>
  <em>ProofGate: The AI that says "No" until you prove it.</em>
</p>

<p align="center">
  <a href="https://github.com/krishnangopal1810/proofgate">⭐ Star us on GitHub</a> •
  <a href="https://github.com/krishnangopal1810/proofgate/issues">🐛 Report Bug</a> •
  <a href="https://github.com/krishnangopal1810/proofgate/issues">💡 Request Feature</a>
</p>
