# PRD: ProofGate — Multi-Agent Judgment System for Financial Compliance (Hackathon Winner Build)

**Owner:** Krishnan  
**Audience:** Coding agent(s) implementing MVP end-to-end  
**Timebox:** Hackathon (1–2 engineers)  
**Demo constraint:** A single coherent end-to-end workflow that can be run live in **< 90 seconds**

---

## 0) What we are optimizing for (maps 1:1 to judging criteria)

This PRD is explicitly engineered to maximize:

1) **Clarity of idea**  
   - One sentence: “Ask if you can book revenue now; ProofGate either approves, rejects, or refuses due to missing evidence—always with citations.”

2) **Track alignment (multi-agent necessity)**  
   - Multi-agent is essential because the decision requires **conflicting objectives**:
     - permissive policy interpretation vs conservative risk vs strict evidence sufficiency
   - Judge resolves conflict via **deterministic rules** (not vibes)

3) **Technical execution**  
   - Strict JSON schemas, citation whitelist enforcement, replayable trace, golden tests

4) **Completeness (E2E workflow)**  
   - A single screen app with doc pack → question → retrieval → agent debate → final JSON verdict → attach evidence → rerun flip

5) **Impact & insight**  
   - High-stakes “fail-closed gate” that prevents unsafe financial actions  
   - Insight: The product is a governed decision workflow, not “RAG Q&A”

---

## 1) One-liner (must be used everywhere)

**ProofGate is a fail-closed multi-agent “judgment layer” that decides whether a financial action is allowed, risky, or missing evidence—returning a structured verdict with clickable citations and a replayable decision trace.**

---

## 2) Problem statement (Clarity of idea)

### The precise problem
Finance/compliance teams constantly face questions like:
> “Can we recognize ₹12Cr revenue this quarter for this customer?”

These decisions are hard because:
- Policies and contracts have nuanced clauses (acceptance, termination, refunds)
- Evidence is incomplete or scattered (emails, UAT signoff, go-live logs)
- Humans miss edge cases and documentation → audit issues and reversals

### What ProofGate achieves (explicit)
Given a proposed action + a small document pack, ProofGate:
1) pulls the relevant clauses and evidence excerpts
2) runs agents that intentionally disagree
3) produces a final **verdict**:
- `APPROVE` (allowed now)
- `REJECT` (not allowed now)
- `INSUFFICIENT_EVIDENCE` (fail-closed until proof is provided)

…and returns a checklist of conditions/evidence with **citations**.

---

## 3) Target user & demo CUJ (Completeness)

### Persona
Revenue accounting / finance controller / deal desk reviewer.

### Single canonical user journey (the only one we ship)
**Goal:** Make the <90s demo impossible to misunderstand.

1) User asks: “Can we recognize ₹12Cr revenue this quarter for Customer K?”
2) ProofGate retrieves up to 6 excerpts:
   - 2 policy clauses
   - 2 contract clauses
   - 2 evidence snippets
3) Agents disagree:
   - Policy Agent: `YES_CONDITIONAL`
   - Risk Agent: `NO` or `YES_CONDITIONAL`
   - Evidence Agent: `MISSING`
4) Judge outputs `INSUFFICIENT_EVIDENCE` (or `REJECT` if hard-stop clause)
5) User attaches one missing evidence document (acceptance email / go-live log)
6) Rerun flips verdict (or materially updates confidence/conditions)
7) Trace log shows run hash + replayability

**Definition of success:** A judge watching the demo can retell it in one sentence.

---

## 4) Track alignment: Why multi-agent is necessary (not theatre)

### Why one prompt is insufficient (what we must demonstrate)
A single prompt tends to:
- collapse policy interpretation, risk appetite, and evidence sufficiency into one blob
- hide internal uncertainty
- hallucinate missing facts or citations

### Multi-agent decomposition (the minimum set)
- **Policy Agent (permissive, conditional):** What is allowed by policy + contract *if* requirements are met?
- **Risk Agent (conservative):** What would cause reversal/audit blow-up? Where are hard-stops?
- **Evidence Agent (strict, fail-closed):** Do we have direct proof for each required fact?
- **Judge Agent (deterministic):** Resolves conflict with explicit rules:
  - hard-stop violations → REJECT
  - missing critical evidence → INSUFFICIENT_EVIDENCE
  - allowed + evidence sufficient + no veto → APPROVE

### The “alignment proof” that must be visible in UI
- stance pills for each agent
- explicit “rule applied” line by Judge
- the verdict changes when evidence is added

---

## 5) Product principles (Technical execution guardrails)

1) **Fail-closed always.** Missing critical evidence → `INSUFFICIENT_EVIDENCE`.  
2) **No invented facts.** Unknown stays unknown.  
3) **No invented citations.** Agents can cite only provided excerpt IDs.  
4) **Strict structured outputs.** JSON schema validation + retry.  
5) **Deterministic trace.** Replays identical inputs with cached outputs.  
6) **Minimal UI.** One screen, no slides.

---

## 6) User experience spec (Completeness + Clarity)

### Single-screen layout (mandatory)
**Top bar**
- Question input
- Toggle: “Deterministic Mode: ON”
- Run button, run_id, latency indicator, replay badge

**Left panel: Doc Pack**
- Policy docs
- Contract docs
- Evidence docs
- “Attach evidence” button

**Center: Relevant excerpts (max 6)**
Each excerpt begins with:
- `[CITE=POL-004] ...`
- `[CITE=CON-002] ...`
- `[CITE=EVI-001] ...`

Clicking citations highlights the excerpt.

**Right: Agent cards**
- Policy Agent (stance + 2 bullets)
- Risk Agent (stance + 2 risk flags)
- Evidence Agent (stance + missing facts)
- Judge Agent (verdict + rule applied)

**Bottom**
- Final verdict JSON
- Collapsible Trace Log: input_hash, prompt versions, per-agent output hashes, final hash

---

## 7) Core outputs (Clarity + Technical execution)

### Final verdict schema (must match exactly)
```json
{
  "verdict": "APPROVE" | "REJECT" | "INSUFFICIENT_EVIDENCE",
  "confidence": 0-1,
  "violations": ["..."],
  "conditions_to_allow": ["..."],
  "citations": ["CITE TOKENS ONLY"]
}
```

Agent outputs (strict JSON, versioned prompt files)
	•	Policy Agent JSON
	•	Risk Agent JSON
	•	Evidence Agent JSON
	•	Judge Agent JSON

Prompts are stored under /prompts/*.txt and loaded at runtime (no drift).

⸻

## 8) Functional requirements (Technical execution + Completeness)

FR1 — Document ingestion (synthetic pack)
	•	Input files: .md / .txt (avoid PDF OCR in hackathon)
	•	Chunk into excerpt blocks
	•	Assign stable excerpt IDs: POL-###, CON-###, EVI-###
	•	Each excerpt text MUST start with [CITE=TYPE-###]

Acceptance criteria
	•	Same content => same excerpt IDs
	•	Excerpts are readable and citeable in UI

FR2 — Retrieval (max 6 excerpts)
	•	For a question, retrieve:
	•	2 policy excerpts
	•	2 contract excerpts
	•	2 evidence excerpts
	•	Return excerpt IDs and text

Acceptance criteria
	•	Excerpts appear in UI center panel
	•	Excerpt IDs included in trace input_hash

FR3 — Agent orchestration
	•	Build “Context Pack” containing:
	•	RUN_ID
	•	QUESTION
	•	PROPOSED_ACTION_JSON
	•	POLICY_EXCERPTS_TEXT
	•	CONTRACT_EXCERPTS_TEXT
	•	EVIDENCE_EXCERPTS_TEXT
	•	Run Policy/Risk/Evidence in parallel
	•	Validate JSON + enforce citation whitelist
	•	Run Judge deterministically

Acceptance criteria
	•	Invalid JSON retried once, else SYSTEM_ERROR
	•	Any hallucinated citation => output rejected and retried once, else fail hard

FR4 — Citation whitelist enforcement (critical)

For each agent output:
	•	Extract citations field (and any nested citations)
	•	Verify every cite token is in the provided excerpt set
	•	If not: retry once with “INVALID_CITATIONS: allowed=…”
	•	If still invalid: fail with SYSTEM_ERROR

Acceptance criteria
	•	0 hallucinated citations in golden tests
	•	Max 1 retry allowed before fail-closed

FR4a — Factual grounding enforcement (no invented facts)

Agents may ONLY state facts that appear in the provided excerpts:
	•	Prompts explicitly instruct: "Only state what excerpts contain. If information is not present, mark as UNKNOWN or MISSING."
	•	Agents must not infer, assume, or fabricate details beyond excerpt text
	•	Any claim without a corresponding citation is suspect and should use hedging language or be omitted

Acceptance criteria
	•	Agent outputs reference only excerpt-sourced facts
	•	Missing information explicitly flagged (not assumed)

FR4b — Excerpt fidelity check (misquote prevention)

When an agent cites an excerpt:
	•	The claim must accurately reflect the excerpt's meaning
	•	Gross mischaracterization = guardrail violation
	•	Implementation: Semantic similarity check OR manual review flag for high-stakes verdicts

Acceptance criteria
	•	No verdict relies on misquoted excerpt content

FR5 — Deterministic trace + replay cache

Compute:
input_hash = sha256(question + sorted_excerpt_ids + evidence_doc_ids + prompt_versions)

If deterministic mode ON:
	•	return cached outputs if present
	•	else compute and store

Trace stores:
	•	run_id, input_hash, excerpt_ids, prompt versions
	•	per-agent output hashes
	•	final output hash
	•	replayed: true/false

Acceptance criteria
	•	Same inputs => replayed outputs, identical hashes

FR6 — Golden scenario pack (completeness proof)

Ship a deterministic synthetic pack ensuring:
	•	Scenario A: Missing acceptance => INSUFFICIENT_EVIDENCE
	•	Scenario B: Add acceptance => flips to APPROVE (or materially changes confidence/conditions)
	•	Scenario C: Hard-stop clause => REJECT

Acceptance criteria
	•	npm test or pytest runs golden scenarios and asserts expected verdicts + citations count

⸻

## 9) Minimal data model (Technical execution)

Document

{
  "doc_id": "string",
  "doc_type": "policy|contract|evidence",
  "title": "string",
  "content_hash": "string"
}

ExcerptBlock

{
  "excerpt_id": "POL-004",
  "cite_token": "[CITE=POL-004]",
  "doc_id": "string",
  "doc_type": "policy|contract|evidence",
  "text": "string"
}

RunTrace

{
  "run_id": "string",
  "input_hash": "string",
  "excerpt_ids": ["POL-004","CON-002","EVI-001"],
  "prompt_versions": {"policy":"v1","risk":"v1","evidence":"v1","judge":"v1"},
  "agent_output_hashes": {"policy":"...","risk":"...","evidence":"...","judge":"..."},
  "final_output_hash": "...",
  "replayed": false
}


⸻

## 10) Reference implementation plan (Technical execution)

Recommended stack (fastest)

Next.js + Node/TypeScript monorepo:
	•	UI + API routes
	•	Local file storage or sqlite for docs + runs
	•	Simple vector store (in-memory or sqlite) for embeddings

Required modules
	•	/ingest: chunking, stable IDs
	•	/retrieve: embedding + similarity search
	•	/agents: prompt loader, model calls, JSON validation
	•	/guards: citation whitelist + schema checks
	•	/trace: hashing, caching, run persistence
	•	/ui: single screen

⸻

## 11) Demo spec (Completeness + Impact & insight)

90s demo script (word-for-word)

“I’m asking a question finance teams hate: ‘Can we recognize ₹12Cr revenue this quarter for Customer K?’
ProofGate retrieves the controlling clauses from our policy and the customer contract, plus what evidence we currently have.
Now the agents disagree: policy says it’s possible but conditional, risk flags a reversal clause, and evidence says we’re missing acceptance proof.
The judge fails closed: verdict is INSUFFICIENT_EVIDENCE, with a checklist of exactly what to attach—each item has citations.
Now I attach the signed acceptance email. Same question, rerun.
Verdict flips, confidence increases, and every claim is backed by clickable citations.
Finally, here’s the trace: same inputs produce the same output hash, so reviewers can replay the decision.”

On-screen must-have checklist
	•	retrieved excerpts visible with cite tokens
	•	agent stances visible
	•	judge “rule applied” line visible
	•	final JSON visible
	•	attach evidence + rerun visible
	•	trace log visible

⸻

12) Impact & insight (what we claim + what we show)

Claim (impact)

This prevents unsafe revenue recognition by turning judgment into:
	•	evidence-gated decisions
	•	consistent policy application
	•	auditable trace artifacts

Insight (non-triviality)

The novelty is a decision workflow:
	•	competing objectives (policy vs risk vs evidence)
	•	deterministic resolution rules
	•	refusal + conditions to allow
	•	reproducibility via trace

Success metric in demo: Judges immediately say: “It refuses without proof.”

⸻

## 13) Definition of Done (Winning bar)

We are done when:
	•	One command runs the app
	•	One screen shows the full E2E workflow
	•	Scenario A -> INSUFFICIENT_EVIDENCE
	•	Attach one doc -> Scenario B flips to APPROVE (or strongly changes confidence/conditions)
	•	Scenario C -> REJECT
	•	0 hallucinated citations (guard enforced)
	•	Demo completes in <90 seconds, reliably

⸻

## 14) Repo structure (required)

/prompts
  policy_agent_v1.txt
  risk_agent_v1.txt
  evidence_agent_v1.txt
  judge_agent_v1.txt
/data/docs
  policy_pack.md
  contract_customer_k.md
  contract_customer_m.md
  evidence_invoice.md
  evidence_project_tracker.md
  evidence_acceptance_email.md
/tests/golden
  scenario_insufficient_evidence.json
  scenario_flip_to_approve.json
  scenario_reject.json
/src
  ingest/
  retrieve/
  agents/
  guards/
  trace/
  ui/
README.md


⸻

15) Immediate next step (implementation unblocker)

To start coding today, implement in this order:
	1.	Ingestion: stable excerpt IDs with [CITE=...]
	2.	Retrieval: topK excerpts per type (max 6)
	3.	Orchestration: 3 agents parallel + judge
	4.	Guards: citation whitelist + schema validation + retry-once
	5.	Trace: input_hash + replay cache
	6.	UI polish: one screen + highlight citations + evidence attach rerun

⸻


If you want, I can also output the **exact Golden Doc Pack texts** (policy + 2 contracts + evidence docs) with pre-planned chunk boundaries and cite IDs so your app deterministically produces:
- INSUFFICIENT_EVIDENCE → attach acceptance → APPROVE,
- plus a separate REJECT scenario with a hard-stop clause.

That’s the single biggest lever to “win by a margin,” because it makes your demo reliable and satisfying every time.