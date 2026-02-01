// ProofGate Frontend Application
import { runJudgment, JudgeResponse, AgentOutput } from './api';

// Import styles
import './styles/variables.css';
import './styles/base.css';
import './styles/components.css';
import './styles/animations.css';

// DOM Elements
const questionInput = document.getElementById('questionInput') as HTMLTextAreaElement;
const acceptanceToggle = document.getElementById('acceptanceToggle') as HTMLInputElement;
const judgeButton = document.getElementById('judgeButton') as HTMLButtonElement;
const pipelineSection = document.getElementById('pipelineSection') as HTMLElement;
const flowArrow = document.getElementById('flowArrow') as HTMLElement;

// Agent cards
const policyAgent = document.getElementById('policyAgent') as HTMLElement;
const riskAgent = document.getElementById('riskAgent') as HTMLElement;
const evidenceAgent = document.getElementById('evidenceAgent') as HTMLElement;
const judgeCard = document.getElementById('judgeCard') as HTMLElement;

// Verdict elements
const ruleApplied = document.getElementById('ruleApplied') as HTMLElement;
const verdictBadge = document.getElementById('verdictBadge') as HTMLElement;
const violationsList = document.getElementById('violationsList') as HTMLElement;
const conditionsList = document.getElementById('conditionsList') as HTMLElement;

// Panels
const evidenceContent = document.getElementById('evidenceContent') as HTMLElement;
const traceContent = document.getElementById('traceContent') as HTMLElement;

// Sidebar & Tooltip
const evidenceSidebar = document.getElementById('evidenceSidebar') as HTMLElement;
const sidebarClose = document.getElementById('sidebarClose') as HTMLElement;
const sidebarContent = document.getElementById('sidebarContent') as HTMLElement;
const sidebarBackdrop = document.getElementById('sidebarBackdrop') as HTMLElement;
const citationTooltip = document.getElementById('citationTooltip') as HTMLElement;

// Knowledge Base
const documentCount = document.getElementById('documentCount') as HTMLElement;
const knowledgeContent = document.getElementById('knowledgeContent') as HTMLElement;

// State
let isLoading = false;
let currentExcerpts: JudgeResponse['excerpts_used'] = [];
let knowledgeBaseExcerpts: JudgeResponse['excerpts_used'] = [];

// Excerpt type definitions for easier lookup
interface ExcerptMap {
    [key: string]: {
        id: string;
        type: string;
        content: string;
    };
}
let excerptMap: ExcerptMap = {};

// Initialize
function init(): void {
    judgeButton.addEventListener('click', handleJudge);

    // Load knowledge base on page load
    loadKnowledgeBase();

    // Sidebar controls
    sidebarClose?.addEventListener('click', closeSidebar);
    sidebarBackdrop?.addEventListener('click', closeSidebar);

    // Setup expand buttons for rationale
    document.querySelectorAll('.expand-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const card = (e.target as HTMLElement).closest('.agent-card');
            const rationale = card?.querySelector('.agent-rationale');
            const isExpanded = rationale?.classList.contains('expanded');

            if (rationale) {
                rationale.classList.toggle('expanded');
                (e.target as HTMLElement).textContent = isExpanded ? '▼ Show Rationale' : '▲ Hide Rationale';
            }
        });
    });

    // Global event delegation for citation badges
    document.addEventListener('click', handleCitationClick);
    document.addEventListener('mouseover', handleCitationHover);
    document.addEventListener('mouseout', handleCitationHoverOut);

    // Handle knowledge doc expand button clicks
    document.addEventListener('click', handleKnowledgeDocClick);

    // Close tooltip on scroll
    document.addEventListener('scroll', () => hideTooltip(), true);
}

// Load knowledge base documents on init
async function loadKnowledgeBase(): Promise<void> {
    try {
        const response = await fetch('/api/excerpts');
        if (!response.ok) throw new Error('Failed to fetch excerpts');

        const data = await response.json();

        // Flatten all excerpts from the response
        const allExcerpts: JudgeResponse['excerpts_used'] = [];
        if (data.excerpts) {
            for (const key of Object.keys(data.excerpts)) {
                const docExcerpts = data.excerpts[key];
                if (Array.isArray(docExcerpts)) {
                    // Map text_preview to text if text is missing (API returns text_preview for /api/excerpts)
                    const mappedExcerpts = docExcerpts.map((e: Record<string, unknown>) => ({
                        ...e,
                        text: (e.text as string) || (e.text_preview as string) || ''
                    })) as JudgeResponse['excerpts_used'];
                    allExcerpts.push(...mappedExcerpts);
                }
            }
        }

        knowledgeBaseExcerpts = allExcerpts;
        displayKnowledgeBase(allExcerpts);

        // Build excerpt map for tooltips immediately
        buildExcerptMap(allExcerpts);

    } catch (error) {
        console.error('Failed to load knowledge base:', error);
        documentCount.textContent = 'Error loading';
        knowledgeContent.innerHTML = '<p class="knowledge-loading" style="color: var(--verdict-reject);">Failed to load documents</p>';
    }
}

// Display knowledge base documents
function displayKnowledgeBase(excerpts: JudgeResponse['excerpts_used']): void {
    if (!excerpts || excerpts.length === 0) {
        documentCount.textContent = '0 documents';
        knowledgeContent.innerHTML = '<p class="knowledge-loading">No documents loaded</p>';
        return;
    }

    documentCount.textContent = `${excerpts.length} documents`;

    knowledgeContent.innerHTML = excerpts.map(excerpt => {
        const type = getExcerptType(excerpt.excerpt_id || '');
        const typeClass = excerpt.doc_type || type.toLowerCase().replace(' document', '');
        const title = getDocTitle(excerpt.excerpt_id || '', excerpt.doc_id || '');
        const preview = (excerpt.text || '').replace(/#+\s*/g, '').replace(/\n/g, ' ').substring(0, 100);

        return `
            <div class="knowledge-doc" data-id="${excerpt.excerpt_id}">
                <span class="knowledge-doc-badge ${typeClass}">${excerpt.excerpt_id}</span>
                <div class="knowledge-doc-info">
                    <div class="knowledge-doc-title">${title}</div>
                    <div class="knowledge-doc-preview">${preview}...</div>
                </div>
                <span class="knowledge-doc-expand" data-id="${excerpt.excerpt_id}">View ▶</span>
            </div>
        `;
    }).join('');
}

// Get human-readable title for document
function getDocTitle(id: string, docId: string): string {
    const titles: Record<string, string> = {
        'POL-001': 'General Revenue Recognition Principles',
        'POL-002': 'Software License Revenue Guidelines',
        'CON-001': 'Customer K Contract - Terms & Value',
        'CON-002': 'Customer K Contract - Delivery & Acceptance',
        'EVI-001': 'Invoice INV-2025-042',
        'EVI-002': 'Implementation Project Tracker',
        'EVI-003': 'Customer Acceptance Email',
    };
    return titles[id] || docId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

// Handle knowledge doc expand click
function handleKnowledgeDocClick(e: Event): void {
    const expandBtn = (e.target as HTMLElement).closest('.knowledge-doc-expand');
    if (!expandBtn) return;

    const docId = expandBtn.getAttribute('data-id');
    if (!docId) return;

    // Use the knowledge base excerpts if we haven't run judgment yet
    const excerpts = currentExcerpts.length > 0 ? currentExcerpts : knowledgeBaseExcerpts;
    currentExcerpts = excerpts;
    buildExcerptMap(excerpts);

    openSidebar(docId);
}

// Handle citation click - open sidebar
function handleCitationClick(e: Event): void {
    const badge = (e.target as HTMLElement).closest('.citation-badge');
    if (!badge) return;

    const citationId = badge.textContent?.trim() || '';
    openSidebar(citationId);
}

// Handle citation hover - show tooltip
function handleCitationHover(e: Event): void {
    const badge = (e.target as HTMLElement).closest('.citation-badge');
    if (!badge) return;

    const citationId = badge.textContent?.trim() || '';
    const excerpt = excerptMap[citationId];

    if (excerpt) {
        showTooltip(badge as HTMLElement, excerpt);
    }
}

// Handle citation hover out - hide tooltip
function handleCitationHoverOut(e: Event): void {
    const badge = (e.target as HTMLElement).closest('.citation-badge');
    if (!badge) return;

    hideTooltip();
}

// Show tooltip
function showTooltip(badge: HTMLElement, excerpt: { id: string; type: string; content: string }): void {
    const tooltipId = citationTooltip.querySelector('.tooltip-id');
    const tooltipType = citationTooltip.querySelector('.tooltip-type');
    const tooltipContent = citationTooltip.querySelector('.tooltip-content');

    if (tooltipId) tooltipId.textContent = excerpt.id;
    if (tooltipType) tooltipType.textContent = excerpt.type;
    if (tooltipContent) tooltipContent.textContent = truncateText(excerpt.content, 300);

    // Position tooltip near badge
    const rect = badge.getBoundingClientRect();
    const tooltipWidth = 320;

    // Prefer bottom-right, but adjust if near edge
    let left = rect.right + 8;
    let top = rect.top;

    if (left + tooltipWidth > window.innerWidth - 20) {
        left = rect.left - tooltipWidth - 8;
    }
    if (left < 20) {
        left = rect.left;
        top = rect.bottom + 8;
    }

    citationTooltip.style.left = `${left}px`;
    citationTooltip.style.top = `${top}px`;
    citationTooltip.classList.add('visible');
}

// Hide tooltip
function hideTooltip(): void {
    citationTooltip.classList.remove('visible');
}

// Open sidebar with citation details
function openSidebar(highlightId?: string): void {
    // Build sidebar content
    let html = '';

    if (currentExcerpts && currentExcerpts.length > 0) {
        html = currentExcerpts.map(excerpt => {
            const isHighlighted = highlightId && excerpt.excerpt_id === highlightId;
            const type = getExcerptType(excerpt.excerpt_id || '');
            return `
        <div class="sidebar-document ${isHighlighted ? 'highlighted' : ''}" data-id="${excerpt.excerpt_id}">
          <div class="document-header">
            <span class="document-id">${excerpt.excerpt_id || 'Unknown'}</span>
            <span class="document-type">${type}</span>
          </div>
          <div class="document-content">${excerpt.text || 'No content available.'}</div>
        </div>
      `;
        }).join('');
    } else {
        html = '<p class="sidebar-placeholder">No evidence documents available.</p>';
    }

    sidebarContent.innerHTML = html;

    // Show sidebar
    evidenceSidebar.classList.add('open');
    sidebarBackdrop.classList.add('visible');

    // Scroll to highlighted document
    if (highlightId) {
        setTimeout(() => {
            const highlighted = sidebarContent.querySelector('.highlighted');
            highlighted?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

// Close sidebar
function closeSidebar(): void {
    evidenceSidebar.classList.remove('open');
    sidebarBackdrop.classList.remove('visible');
}

// Get excerpt type from ID
function getExcerptType(id: string): string {
    if (id.startsWith('POL')) return 'Policy Document';
    if (id.startsWith('CON')) return 'Contract Clause';
    if (id.startsWith('EVI')) return 'Evidence Document';
    return 'Document';
}

// Build excerpt map for quick lookup
function buildExcerptMap(excerpts: JudgeResponse['excerpts_used']): void {
    excerptMap = {};
    if (!excerpts) return;

    excerpts.forEach(excerpt => {
        if (excerpt.excerpt_id) {
            excerptMap[excerpt.excerpt_id] = {
                id: excerpt.excerpt_id,
                type: getExcerptType(excerpt.excerpt_id),
                content: excerpt.text || ''
            };
        }
    });
}

// Handle judgment request
async function handleJudge(): Promise<void> {
    if (isLoading) return;

    const question = questionInput.value.trim();
    if (!question) {
        alert('Please enter a question');
        return;
    }

    try {
        setLoading(true);
        resetUI();
        showPipeline();

        // Start agent animations
        await animateAgentsRunning();

        // Make API call
        console.log('Sending request:', { question, include_acceptance_email: acceptanceToggle.checked });
        const response = await runJudgment({
            question,
            include_acceptance_email: acceptanceToggle.checked,
        });
        console.log('Received response:', response);

        // Store excerpts for sidebar/tooltip
        currentExcerpts = response.excerpts_used || [];
        buildExcerptMap(currentExcerpts);

        // Update UI with results
        await displayResults(response);

    } catch (error) {
        console.error('Judgment failed:', error);
        showError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
        setLoading(false);
    }
}

// Set loading state
function setLoading(loading: boolean): void {
    isLoading = loading;
    judgeButton.disabled = loading;
    judgeButton.classList.toggle('loading', loading);
}

// Reset UI to initial state
function resetUI(): void {
    // Reset excerpts
    currentExcerpts = [];
    excerptMap = {};
    closeSidebar();

    // Reset agent cards
    [policyAgent, riskAgent, evidenceAgent].forEach(agent => {
        agent.classList.remove('visible', 'running', 'complete');
        const status = agent.querySelector('.agent-status');
        if (status) {
            status.innerHTML = '<span class="status-icon">⏳</span><span class="status-text">Waiting...</span>';
        }
        const stance = agent.querySelector('.agent-stance');
        if (stance) {
            stance.setAttribute('data-stance', '');
            const value = stance.querySelector('.stance-value');
            if (value) value.textContent = '—';
        }
        const conditions = agent.querySelector('.agent-conditions');
        if (conditions) conditions.innerHTML = '';
        const citations = agent.querySelector('.agent-citations');
        if (citations) citations.innerHTML = '';
        const rationale = agent.querySelector('.agent-rationale');
        if (rationale) {
            rationale.classList.remove('expanded');
            rationale.innerHTML = '';
        }
        const expandBtn = agent.querySelector('.expand-button') as HTMLElement;
        if (expandBtn) expandBtn.textContent = '▼ Show Rationale';
    });

    // Reset judge card
    judgeCard.classList.remove('visible');
    ruleApplied.classList.remove('visible');
    ruleApplied.textContent = '';
    ruleApplied.style.background = '';
    ruleApplied.style.color = '';
    verdictBadge.className = 'verdict-badge';
    verdictBadge.querySelector('.verdict-text')!.textContent = '—';
    violationsList.innerHTML = '';
    conditionsList.innerHTML = '';

    // Reset flow arrow
    flowArrow.classList.remove('visible', 'active');

    // Reset panels
    evidenceContent.innerHTML = '<p class="panel-placeholder">Loading evidence...</p>';
    traceContent.innerHTML = '<p class="panel-placeholder">Loading trace...</p>';
}

// Show pipeline section
function showPipeline(): void {
    pipelineSection.classList.add('visible');
}

// Animate agents running
async function animateAgentsRunning(): Promise<void> {
    const agents = [policyAgent, riskAgent, evidenceAgent];

    // Show agents with stagger
    for (let i = 0; i < agents.length; i++) {
        await delay(100);
        agents[i].classList.add('visible', 'running');
        const status = agents[i].querySelector('.agent-status');
        if (status) {
            status.innerHTML = '<span class="status-icon">⏳</span><span class="status-text">Analyzing...</span>';
        }
    }

    // Show flow arrow
    await delay(200);
    flowArrow.classList.add('visible', 'active');

    // Show judge card waiting
    await delay(100);
    judgeCard.classList.add('visible');
}

// Display results from API
async function displayResults(response: JudgeResponse): Promise<void> {
    const { verdict, agent_outputs, trace, excerpts_used } = response;

    if (!agent_outputs) {
        throw new Error('Missing agent outputs in response');
    }

    // Update agent cards with results
    await updateAgentCard(policyAgent, agent_outputs.policy, 100);
    await updateAgentCard(riskAgent, agent_outputs.risk, 200);
    await updateAgentCard(evidenceAgent, agent_outputs.evidence, 300);

    // Flow arrow active
    flowArrow.classList.add('active');
    await delay(500);

    // Update judge
    await updateJudgeCard(verdict);

    // Update panels
    updateEvidencePanel(excerpts_used);
    updateTracePanel(trace);
}

// Update individual agent card
async function updateAgentCard(card: HTMLElement, output: AgentOutput, delayMs: number): Promise<void> {
    await delay(delayMs);

    card.classList.remove('running');
    card.classList.add('complete');

    if (!output) {
        const status = card.querySelector('.agent-status');
        if (status) status.innerHTML = '<span class="status-icon" style="color:red">✗</span><span class="status-text">Error</span>';
        return;
    }

    // Update status
    const status = card.querySelector('.agent-status');
    if (status) {
        status.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Complete</span>';
    }

    // Update stance
    const stance = card.querySelector('.agent-stance');
    if (stance) {
        stance.setAttribute('data-stance', output.stance || 'UNKNOWN');
        const value = stance.querySelector('.stance-value');
        if (value) value.textContent = (output.stance || 'UNKNOWN').replace('_', ' ');
    }

    // Update conditions
    const conditionsEl = card.querySelector('.agent-conditions');
    if (conditionsEl && output.conditions && Array.isArray(output.conditions) && output.conditions.length > 0) {
        conditionsEl.innerHTML = `
      <strong>Conditions:</strong>
      <ul>${output.conditions.map(c => `<li>${c}</li>`).join('')}</ul>
    `;
    }

    // Update hard stops
    if (conditionsEl && output.hard_stops && Array.isArray(output.hard_stops) && output.hard_stops.length > 0) {
        conditionsEl.innerHTML += `
      <strong style="color: var(--verdict-reject);">Hard Stops:</strong>
      <ul>${output.hard_stops.map(h => `<li style="color: var(--verdict-reject-light);">${h}</li>`).join('')}</ul>
    `;
    }

    // Update citations - make them interactive
    const citationsEl = card.querySelector('.agent-citations');
    if (citationsEl && output.citations && Array.isArray(output.citations) && output.citations.length > 0) {
        citationsEl.innerHTML = output.citations
            .map(c => {
                const type = c.split('-')[0]; // POL, CON, EVI
                return `<span class="citation-badge" data-type="${type}" data-citation="${c}">${c}</span>`;
            })
            .join('');
    }

    // Update rationale
    const rationaleEl = card.querySelector('.agent-rationale');
    if (rationaleEl && output.rationale) {
        rationaleEl.textContent = output.rationale;
    }
}

// Update judge card with verdict
async function updateJudgeCard(verdict: JudgeResponse['verdict']): Promise<void> {
    if (!verdict) return;

    // Update status
    const status = judgeCard.querySelector('.judge-status');
    if (status) {
        status.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Resolved</span>';
    }

    // Show rule applied
    ruleApplied.textContent = verdict.rule_applied || 'No rule info';
    ruleApplied.classList.add('visible');

    await delay(300);

    // Show verdict badge with animation
    const verdictText = verdictBadge.querySelector('.verdict-text');
    if (verdictText) {
        verdictText.textContent = (verdict.verdict || 'UNKNOWN').replace(/_/g, ' ');
    }
    verdictBadge.className = `verdict-badge ${verdict.verdict || 'UNKNOWN'}`;

    await delay(100);
    verdictBadge.classList.add('visible');

    // Show violations with citations
    if (verdict.violations && Array.isArray(verdict.violations) && verdict.violations.length > 0) {
        violationsList.innerHTML = `
      <h4>⚠️ Violations</h4>
      <ul>${verdict.violations.map(v => `<li>${v}</li>`).join('')}</ul>
    `;
    }

    // Show conditions to allow
    if (verdict.conditions_to_allow && Array.isArray(verdict.conditions_to_allow) && verdict.conditions_to_allow.length > 0) {
        conditionsList.innerHTML = `
      <h4>📋 Conditions to Approve</h4>
      <ul>${verdict.conditions_to_allow.map(c => `<li>${c}</li>`).join('')}</ul>
    `;
    }

    // Show verdict-level citations
    if (verdict.citations && Array.isArray(verdict.citations) && verdict.citations.length > 0) {
        const citationsHtml = verdict.citations
            .map(c => {
                const type = c.split('-')[0];
                return `<span class="citation-badge" data-type="${type}" data-citation="${c}">${c}</span>`;
            })
            .join(' ');

        // Add citation row after conditions
        const citationRow = document.createElement('div');
        citationRow.className = 'verdict-citations';
        citationRow.innerHTML = `
      <h4>📎 Supporting Evidence</h4>
      <div class="citation-list">${citationsHtml}</div>
    `;

        // Find judge card content area and append
        const existingCitations = judgeCard.querySelector('.verdict-citations');
        if (existingCitations) existingCitations.remove();
        judgeCard.appendChild(citationRow);
    }
}

// Update evidence panel
function updateEvidencePanel(excerpts: JudgeResponse['excerpts_used']): void {
    if (!excerpts || !Array.isArray(excerpts) || excerpts.length === 0) {
        evidenceContent.innerHTML = '<p class="panel-placeholder">No evidence excerpts used.</p>';
        return;
    }

    evidenceContent.innerHTML = excerpts.map(excerpt => {
        const type = getExcerptType(excerpt.excerpt_id || '');
        return `
    <div class="excerpt-card cited">
      <div class="excerpt-header">
        <span class="excerpt-id">${excerpt.excerpt_id || 'ID?'}</span>
        <span class="excerpt-status">${type}</span>
      </div>
      <div class="excerpt-content">${truncateText(excerpt.text, 200)}</div>
    </div>
  `;
    }).join('');
}

// Update trace panel
function updateTracePanel(trace: JudgeResponse['trace']): void {
    if (!trace) {
        traceContent.innerHTML = '<p class="panel-placeholder">No trace data available.</p>';
        return;
    }

    traceContent.innerHTML = `
    <div class="trace-grid">
      <div class="trace-item">
        <div class="trace-label">Run ID</div>
        <div class="trace-value">${trace.run_id || 'N/A'}</div>
      </div>
      <div class="trace-item">
        <div class="trace-label">Input Hash</div>
        <div class="trace-value">${(trace.input_hash || '').substring(0, 16)}...</div>
      </div>
      <div class="trace-item">
        <div class="trace-label">Replayed</div>
        <div class="trace-value">${trace.replayed ? '✓ Yes (cached)' : '✗ No (fresh)'}</div>
      </div>
      <div class="trace-item">
        <div class="trace-label">Latency</div>
        <div class="trace-value">${(trace.latency_ms / 1000).toFixed(2)}s</div>
      </div>
      <div class="trace-item">
        <div class="trace-label">Timestamp</div>
        <div class="trace-value">${trace.timestamp ? new Date(trace.timestamp).toLocaleString() : 'N/A'}</div>
      </div>
    </div>
    <div class="trace-hashes">
      <h4>Agent Output Hashes</h4>
      <div class="hash-tree">
        ├─ policy: <span>${trace.agent_output_hashes?.policy?.substring(0, 12) || 'N/A'}...</span><br>
        ├─ risk: <span>${trace.agent_output_hashes?.risk?.substring(0, 12) || 'N/A'}...</span><br>
        ├─ evidence: <span>${trace.agent_output_hashes?.evidence?.substring(0, 12) || 'N/A'}...</span><br>
        └─ judge: <span>${trace.agent_output_hashes?.judge?.substring(0, 12) || 'N/A'}...</span>
      </div>
    </div>
  `;
}

// Show error message
function showError(message: string): void {
    const status = judgeCard.querySelector('.judge-status');
    if (status) {
        status.innerHTML = `<span class="status-icon" style="color: var(--verdict-reject);">✗</span><span class="status-text" style="color: var(--verdict-reject);">Error</span>`;
    }

    ruleApplied.textContent = `Error: ${message}`;
    ruleApplied.classList.add('visible');
    ruleApplied.style.background = 'rgba(239, 68, 68, 0.2)';
    ruleApplied.style.color = 'var(--verdict-reject-light)';

    const verdictText = verdictBadge.querySelector('.verdict-text');
    if (verdictText) {
        verdictText.textContent = 'FAIL CLOSED';
    }
    verdictBadge.className = 'verdict-badge REJECT visible';
}

// Utility: delay
function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Utility: truncate text
function truncateText(text: string | null | undefined, maxLength: number): string {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);
