# ProofGate Frontend Design Document

> **Goal:** Create a visually stunning, single-page demo UI that showcases the multi-agent judgment system's unique value proposition and wins the hackathon.

---

## 🏆 CRITICAL: First-Prize Design Decisions

> These are the **non-negotiable** design choices that differentiate a winning demo from a forgettable one.

### 1. Full-Screen Verdict Reveal (The Theatrical Moment)

When verdicts complete, the screen should have a **dramatic reveal**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                                                                              │
│                                                                              │
│            ╔═══════════════════════════════════════════════════╗            │
│            ║                                                    ║            │
│            ║                    🔴 REJECT                       ║            │
│            ║                                                    ║            │
│            ║     "Formal customer acceptance not obtained"      ║            │
│            ║                                                    ║            │
│            ╚═══════════════════════════════════════════════════╝            │
│                                                                              │
│                        ┌─────────────────────┐                              │
│                        │  📄 Add Evidence    │                              │
│                        │  [See What Changes] │                              │
│                        └─────────────────────┘                              │
│                                                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

Then when they click "Add Evidence" → screen morphs:

```
🔴 REJECT  ───────────────────▶  🟢 APPROVE
(animated transition with particle effects)
```

### 2. Progressive Disclosure (Hide Complexity)

**Default view:** Only verdict + key insight
**On-demand:** Agent details, traces, evidence

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERDICT: REJECT                               │
│              ─────────────────────────                           │
│                                                                  │
│    "Customer acceptance required but not found"                  │
│                                                                  │
│    [▼ Why did 3 agents reach this conclusion?]                  │
│    [▼ What evidence was analyzed?]                              │
│    [▼ View cryptographic audit trace]                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Why:** Judges with 2 minutes see the verdict. Judges who want depth can expand.

---

## 🎯 Design Philosophy

### Hackathon Judging Alignment

| Criterion | How UI Demonstrates It |
|-----------|----------------------|
| **Clarity of idea** | Full-screen verdict reveals the concept instantly |
| **Track alignment** | Agent pipeline animates in real-time showing coordination |
| **Technical execution** | Live API integration with actual verdict responses |
| **Completeness** | Full e2e demo flow in 30 seconds |
| **Impact & insight** | Verdict flip creates instant "aha" moment |

### Core UX Principles

1. **One Screen, One Story** - No navigation, no tabs, everything visible
2. **Show, Don't Tell** - Animate the multi-agent pipeline in real-time
3. **The "Flip" Moment** - Build to the dramatic verdict reversal
4. **Zero Learning Curve** - Works on first visit, no onboarding

---

## 🖼️ Layout: Single Page Hero

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HEADER (Fixed, 60px)                               │
│  🔐 ProofGate          "The AI that says No until you prove it"    [Docs]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌───────────────────────────┐                        │
│                         │   QUESTION INPUT CARD      │                        │
│                         │   ┌─────────────────────┐  │                        │
│                         │   │ Can we recognize... │  │                        │
│                         │   └─────────────────────┘  │                        │
│                         │   [□ Include Acceptance]   │                        │
│                         │   [     🔍 JUDGE      ]    │                        │
│                         └───────────────────────────┘                        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     AGENT PIPELINE VISUALIZATION                      │   │
│  │                                                                       │   │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                │   │
│  │   │   POLICY    │   │    RISK     │   │  EVIDENCE   │                │   │
│  │   │   Agent     │   │   Agent     │   │   Agent     │                │   │
│  │   │  ⏳ / ✓    │   │  ⏳ / ✓    │   │  ⏳ / ✓    │                │   │
│  │   │─────────────│   │─────────────│   │─────────────│                │   │
│  │   │ Stance:     │   │ Stance:     │   │ Stance:     │                │   │
│  │   │ YES_COND    │   │ NO          │   │ MISSING     │                │   │
│  │   └─────────────┘   └─────────────┘   └─────────────┘                │   │
│  │                           │                                           │   │
│  │                           ▼                                           │   │
│  │   ┌─────────────────────────────────────────────────────────────┐    │   │
│  │   │                    JUDGE AGENT                               │    │   │
│  │   │   Rule Applied: RULE_1 - Hard-stop detected                  │    │   │
│  │   │                                                              │    │   │
│  │   │   ┌────────────────────────────────────────────────────┐     │    │   │
│  │   │   │              VERDICT: REJECT                        │     │    │   │
│  │   │   │              🔴 (animated glow)                     │     │    │   │
│  │   │   └────────────────────────────────────────────────────┘     │    │   │
│  │   └─────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      EVIDENCE PANEL (Collapsible)                     │   │
│  │   📄 POL-001: Revenue Recognition Principles      [CITED]            │   │
│  │   📄 CON-002: Delivery and Acceptance             [CITED]            │   │
│  │   📄 EVI-002: Implementation Status               [CITED]            │   │
│  │   📄 EVI-003: Acceptance Email                    [NOT IN CONTEXT]   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      TRACE PANEL (Collapsible)                        │   │
│  │   Run ID: abc12345    Input Hash: 7f3a...    Replayed: ✗             │   │
│  │   Latency: 24.6s      Timestamp: 2026-01-31T21:06:39                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           FOOTER                                             │
│   Built with OpenAI Agents SDK  •  GitHub  •  MIT License                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Visual Design System

### Color Palette

```css
:root {
  /* Primary - Trust/Security */
  --primary-900: #0f172a;      /* Deep navy - backgrounds */
  --primary-700: #334155;      /* Slate - cards */
  --primary-500: #64748b;      /* Muted text */
  
  /* Verdict Colors */
  --verdict-approve: #10b981;   /* Emerald green */
  --verdict-reject: #ef4444;    /* Red */
  --verdict-insufficient: #f59e0b; /* Amber */
  --verdict-conditional: #3b82f6;  /* Blue */
  
  /* Agent Colors */
  --agent-policy: #8b5cf6;      /* Purple - permissive */
  --agent-risk: #f97316;        /* Orange - conservative */
  --agent-evidence: #06b6d4;    /* Cyan - neutral */
  --agent-judge: #fbbf24;       /* Gold - authority */
  
  /* Accents */
  --glow-approve: rgba(16, 185, 129, 0.4);
  --glow-reject: rgba(239, 68, 68, 0.4);
  
  /* Glassmorphism */
  --glass-bg: rgba(30, 41, 59, 0.8);
  --glass-border: rgba(148, 163, 184, 0.2);
}
```

### Typography

```css
/* Google Fonts: Inter + JetBrains Mono */
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Scale */
--text-hero: 3rem;      /* 48px - main headline */
--text-h1: 1.875rem;    /* 30px - section headers */
--text-h2: 1.25rem;     /* 20px - card headers */
--text-body: 1rem;      /* 16px - body text */
--text-small: 0.875rem; /* 14px - captions */
--text-mono: 0.8125rem; /* 13px - code/IDs */
```

### Glassmorphism Cards

```css
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
```

---

## 🧩 Component Specifications

### 1. Question Input Card

```
┌────────────────────────────────────────────────────────┐
│  💬 Ask ProofGate                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Can we recognize ₹12Cr revenue this quarter for  │  │
│  │ Customer K?                                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ☐ Include acceptance email in evidence           │  │
│  │   (Toggle to see verdict flip!)                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │           🔍  RUN JUDGMENT                        │  │
│  │           (Primary action button)                │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**States:**
- **Idle:** Button enabled, ready for input
- **Loading:** Button shows spinner, disabled
- **Error:** Red border on input, error message below

### 2. Agent Card (×3)

```
┌─────────────────────────────────────┐
│  📋 POLICY AGENT                    │  ← Header with icon + color bar
│  ─────────────────────────────────  │
│                                     │
│  Status: ⏳ Running...              │  ← Animated spinner
│          ✓ Complete (2.4s)          │  ← Shows latency on complete
│                                     │
│  ┌─────────────────────────────────┐│
│  │  Stance: YES_CONDITIONAL         ││  ← Highlighted stance badge
│  └─────────────────────────────────┘│
│                                     │
│  Conditions:                        │
│  • Written acceptance from K        │  ← Bullet list
│  • 15 days production use           │
│                                     │
│  Citations: [POL-001] [CON-002]     │  ← Clickable badges
│                                     │
│  [▼ Show Rationale]                 │  ← Expandable detail
└─────────────────────────────────────┘
```

**Animation Sequence:**
1. Card appears with fade-in (staggered 100ms between agents)
2. Spinner animates while agent runs
3. Stance badge slides in from right with pop animation
4. Citations fade in one by one (100ms stagger)

### 3. Judge Card (Hero Element)

```
┌─────────────────────────────────────────────────────────────────┐
│                         ⚖️ JUDGE                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Rule Applied:                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  RULE_1: Hard-stop violation detected                        ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│                    ┌───────────────────────┐                     │
│                    │                       │                     │
│                    │       REJECT          │  ← Large, bold      │
│                    │         🔴            │  ← Animated glow    │
│                    │                       │                     │
│                    └───────────────────────┘                     │
│                                                                  │
│  Violations:                                                     │
│  ⚠️ Formal customer acceptance not obtained (EVI-002)            │
│                                                                  │
│  [📋 View Full Trace]  [🔄 Replay]                               │
└─────────────────────────────────────────────────────────────────┘
```

**Verdict Badge Styling:**

| Verdict | Background | Glow | Icon |
|---------|-----------|------|------|
| APPROVE | `#10b981` | Green pulse | ✓ |
| REJECT | `#ef4444` | Red pulse | ✗ |
| INSUFFICIENT_EVIDENCE | `#f59e0b` | Amber pulse | ⚠️ |
| CONDITIONAL_APPROVE | `#3b82f6` | Blue pulse | ⚡ |

### 4. Evidence Panel

```
┌──────────────────────────────────────────────────────────────────┐
│  📚 Evidence Context                              [▲ Collapse]   │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 📄 POL-001  Revenue Recognition Principles                   │ │
│  │ ──────────────────────────────────────────────────────────── │ │
│  │ Revenue shall be recognized when the following criteria      │ │
│  │ are ALL satisfied:                                           │ │
│  │ • Delivery of goods or services is complete                  │ │
│  │ • Customer acceptance has been obtained...                   │ │
│  │                                                    [CITED ✓] │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 📄 EVI-003  Acceptance Email            [NOT IN CONTEXT]    │ │
│  │ ──────────────────────────────────────────────────────────── │ │
│  │ (Grayed out - not included in current run)                   │ │
│  │                                           [+ Add to Context] │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Citation Highlighting:** When agent cites POL-001, that card glows briefly
- **Context Toggle:** EVI-003 is grayed out until checkbox is toggled
- **Cross-reference:** Click citation badge → scrolls to evidence card

### 5. Trace Panel

```
┌──────────────────────────────────────────────────────────────────┐
│  🔍 Audit Trace                                   [▲ Collapse]   │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  Run ID:      abc12345                                           │
│  Input Hash:  7f3a2b9c... (sha256)        [📋 Copy]              │
│  Replayed:    ✗ (Fresh execution)                                │
│  Timestamp:   2026-01-31T21:06:39.045Z                           │
│  Latency:     24,611ms                                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Agent Output Hashes                                         │ │
│  │  ├─ policy:   4ea52c36...                                    │ │
│  │  ├─ risk:     4f33d89f...                                    │ │
│  │  ├─ evidence: dd1181c0...                                    │ │
│  │  └─ judge:    5c2e2c9b...                                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  [📥 Export JSON]  [🔄 Replay This Trace]                        │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎬 Animation & Micro-Interactions

### Pipeline Flow Animation

```
Timeline (seconds):
0.0s  ─┬─ User clicks "RUN JUDGMENT"
       │  → Button morphs to loading state
       │  → Question card slightly dims
       │
0.2s  ─┼─ Agent cards appear (staggered)
       │  → Policy card fades in
0.3s  ─│  → Risk card fades in
0.4s  ─│  → Evidence card fades in
       │  → All show spinning loaders
       │
0.5s  ─┼─ Animated "data flow" lines appear
       │  → SVG paths from excerpts → agents
       │
~5s   ─┼─ First agent completes (varies)
       │  → Spinner → Checkmark (with pop)
       │  → Stance badge slides in
       │
~8s   ─┼─ All agents complete
       │  → Flow lines animate toward Judge
       │
~10s  ─┼─ Judge card expands
       │  → Rule text types in (typewriter effect)
       │
~11s  ─┼─ VERDICT REVEAL
       │  → Badge scales from 0 → 1.2 → 1.0
       │  → Glow animation starts
       │  → Confetti if APPROVE (optional)
       │
~12s  ─┴─ Trace panel populates
          → Hash values appear with fade
```

### The "Flip" Animation (Key Demo Moment)

When user toggles "Include acceptance email" and re-runs:

```
1. Previous verdict (REJECT) fades out with red glow dimming
2. Evidence panel: EVI-003 card transitions from gray → full color
3. Agent cards reset and re-animate
4. Judge card: 
   - Rule text changes with crossfade
   - Verdict badge morphs: 🔴 REJECT → 🟢 APPROVE
   - Celebratory green pulse animation
5. Optional: subtle "✨" particle effect
```

### Hover States

| Element | Hover Effect |
|---------|-------------|
| Agent Card | Slight lift (translateY -2px), border glow |
| Citation Badge | Scale 1.05, tooltip with full ID |
| Evidence Card | Border highlight in agent color |
| Verdict Badge | Intensify glow animation |
| Copy Button | Icon rotates, shows "Copied!" toast |

---

## 📱 Responsive Breakpoints

| Breakpoint | Layout |
|------------|--------|
| **Desktop (≥1024px)** | 3-column agent cards, side-by-side panels |
| **Tablet (768-1023px)** | 3-column agents, stacked panels |
| **Mobile (≤767px)** | Single column, agents as horizontal scroll |

### Mobile Optimizations
- Agent cards become horizontal swipe carousel
- Evidence/Trace panels collapsed by default
- Verdict badge takes full width
- Touch-friendly button sizes (min 44px)

---

## 🛠️ Technical Implementation

### Recommended Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Framework** | React 18 or Vanilla JS | Keep it simple for hackathon |
| **Styling** | CSS Variables + Vanilla CSS | No build step, fast iteration |
| **Animations** | CSS Keyframes + GSAP (optional) | Smooth, performant |
| **Icons** | Heroicons or Lucide | Modern, tree-shakeable |
| **Build** | Vite | Fast dev server, simple config |

### API Integration

```javascript
// Single endpoint call
async function runJudgment(question, includeAcceptance) {
  const response = await fetch('/api/judge', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      include_acceptance_email: includeAcceptance
    })
  });
  return response.json();
}
```

### State Management (Simple)

```javascript
const state = {
  status: 'idle' | 'loading' | 'success' | 'error',
  question: string,
  includeAcceptance: boolean,
  result: {
    verdict: {...},
    agent_outputs: {...},
    trace: {...},
    excerpts_used: [...]
  },
  error: string | null
};
```

---

## 🏆 Hackathon Demo Script (30 seconds)

| Time | Action | What Judges See |
|------|--------|-----------------|
| 0-5s | "Can we recognize revenue?" | Clear question, toggle OFF |
| 5-15s | Click "Judge" | Multi-agent pipeline animates |
| 15-18s | Verdict appears | 🔴 REJECT with violations |
| 18-22s | "But what if we add evidence?" | Toggle acceptance ON |
| 22-28s | Re-run | Agents re-animate, verdict FLIPS |
| 28-30s | 🟢 APPROVE | "Same question, different evidence" |

**Key Message:** *"The AI said no until we proved it. That's ProofGate."*

---

## 📁 File Structure

```
frontend/
├── index.html              # Single-page entry
├── css/
│   ├── variables.css       # Design tokens
│   ├── base.css            # Reset, typography
│   ├── components.css      # Card, button styles
│   └── animations.css      # Keyframes, transitions
├── js/
│   ├── app.js              # Main application
│   ├── api.js              # API client
│   └── animations.js       # GSAP timeline (optional)
├── assets/
│   └── icons/              # SVG icons
└── README.md               # Setup instructions
```

---

## ✅ Success Criteria

| Metric | Target |
|--------|--------|
| **First Meaningful Paint** | < 1s |
| **Time to Interactive** | < 2s |
| **Demo Complete Flow** | < 30s |
| **Works Without Errors** | 100% |
| **Mobile Responsive** | Yes |
| **"Wow" Moment Visible** | Verdict flip animation |

---

> **Next Step:** Implement this design as a working frontend. Focus on the verdict flip animation—that's the money shot for the hackathon demo.
