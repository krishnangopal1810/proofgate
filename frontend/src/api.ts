// Type definitions for ProofGate API

export interface JudgeRequest {
    question: string;
    include_acceptance_email: boolean;
}

export interface AgentOutput {
    stance: 'YES' | 'NO' | 'YES_CONDITIONAL' | 'MISSING' | 'PRESENT';
    conditions?: string[];
    hard_stops?: string[];
    rationale: string;
    citations: string[];
    confidence?: number;
}

export interface FinalVerdict {
    verdict: 'APPROVE' | 'REJECT' | 'INSUFFICIENT_EVIDENCE' | 'CONDITIONAL_APPROVE' | 'FAIL_CLOSED_ON_ERROR';
    confidence?: number;
    violations?: string[];
    conditions_to_allow?: string[];
    citations?: string[];
    rule_applied: string;
}

export interface ExcerptBlock {
    excerpt_id: string;
    cite_token: string;
    doc_id: string;
    doc_type: string;
    text: string;  // Note: API uses 'text' not 'content'
    doc_name?: string;
    metadata?: Record<string, unknown>;
}

export interface RunTrace {
    run_id: string;
    input_hash: string;
    question: string;
    excerpt_ids: string[];
    prompt_versions: Record<string, string>;
    agent_output_hashes: Record<string, string>;
    final_output_hash: string;
    replayed: boolean;
    timestamp: string;
    latency_ms: number;
}

export interface JudgeResponse {
    run_id: string;
    verdict: FinalVerdict;
    agent_outputs: {
        policy: AgentOutput;
        risk: AgentOutput;
        evidence: AgentOutput;
    };
    trace: RunTrace;
    excerpts_used: ExcerptBlock[];
}

export interface ApiError {
    error: string;
    detail?: string;
}

// API Client
// Uses Vite proxy - see vite.config.ts
const API_BASE_URL = '';

export async function runJudgment(request: JudgeRequest): Promise<JudgeResponse> {
    const response = await fetch(`${API_BASE_URL}/api/judge`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
    });

    if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.detail || error.error || `HTTP ${response.status}`);
    }

    return response.json();
}

export async function getExcerpts(): Promise<{ excerpts: Record<string, ExcerptBlock[]> }> {
    const response = await fetch(`${API_BASE_URL}/api/excerpts`);

    if (!response.ok) {
        throw new Error(`Failed to fetch excerpts: HTTP ${response.status}`);
    }

    return response.json();
}

export async function getTraces(): Promise<{ traces: RunTrace[] }> {
    const response = await fetch(`${API_BASE_URL}/api/traces`);

    if (!response.ok) {
        throw new Error(`Failed to fetch traces: HTTP ${response.status}`);
    }

    return response.json();
}

export async function healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
        throw new Error('API is not available');
    }

    return response.json();
}
