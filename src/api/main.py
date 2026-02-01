"""
ProofGate FastAPI Application

RESTful API for the multi-agent judgment system.
"""

import os
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.orchestrator import ProofGateOrchestrator
from src.ingest import load_all_documents
from src.retrieve import SimpleRetriever
from src.schemas.documents import RunTrace

# Load environment variables
load_dotenv()


# Request/Response Models
class JudgeRequest(BaseModel):
    """Request to run the judgment pipeline."""
    question: str = Field(
        description="The question to evaluate",
        json_schema_extra={"example": "Can we recognize ₹12Cr revenue this quarter for Customer K?"}
    )
    include_acceptance_email: bool = Field(
        default=False,
        description="Whether to include the acceptance email in evidence"
    )


class JudgeResponse(BaseModel):
    """Response from the judgment pipeline."""
    run_id: str
    verdict: dict
    agent_outputs: dict
    trace: dict
    excerpts_used: List[dict] = []
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    agents_loaded: bool


class TraceListResponse(BaseModel):
    """List of traces response."""
    traces: List[dict]
    count: int


# Global state
_orchestrator: Optional[ProofGateOrchestrator] = None
_retriever: Optional[SimpleRetriever] = None
_all_excerpts: dict = {}


async def _get_orchestrator() -> ProofGateOrchestrator:
    """Get or create the orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ProofGateOrchestrator(
            data_dir=Path("./data"),
            deterministic_mode=True,
        )
        await _orchestrator.init()
    return _orchestrator


def _get_retriever(include_acceptance: bool = False) -> SimpleRetriever:
    """Get or create the retriever instance."""
    global _retriever, _all_excerpts
    
    data_dir = Path("./data")
    data = load_all_documents(data_dir)
    
    excerpts_by_type = data['excerpts'].copy()
    
    # Filter out acceptance email if not included
    if not include_acceptance:
        excerpts_by_type['evidence'] = [
            e for e in excerpts_by_type['evidence']
            if e.excerpt_id != 'EVI-003'  # Acceptance email
        ]
    
    # When acceptance email is included, increase evidence limit to include all 3
    evidence_limit = 3 if include_acceptance else 2
    return SimpleRetriever(excerpts_by_type, evidence_limit=evidence_limit)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    global _orchestrator
    _orchestrator = await _get_orchestrator()
    yield
    # Shutdown
    pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ProofGate API",
        description=(
            "Multi-agent judgment system for financial compliance. "
            "Fail-closed, citation-enforced, deterministic."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


app = create_app()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents_loaded=_orchestrator is not None,
    )


@app.post("/api/judge", response_model=JudgeResponse)
async def run_judgment(request: JudgeRequest):
    """
    Run the multi-agent judgment pipeline.
    
    This is the main endpoint that:
    1. Retrieves relevant excerpts
    2. Runs Policy, Risk, Evidence agents in parallel
    3. Validates citations (no hallucinations)
    4. Runs Judge agent for deterministic resolution
    5. Returns structured verdict with trace
    """
    orchestrator = await _get_orchestrator()
    
    # Get retriever with or without acceptance email
    retriever = _get_retriever(
        include_acceptance=request.include_acceptance_email
    )
    
    # Retrieve excerpts
    excerpts = retriever.retrieve(request.question)
    
    # Run judgment pipeline
    try:
        result = await orchestrator.run(request.question, excerpts)
        return JudgeResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Judgment pipeline error: {str(e)}"
        )


@app.post("/api/evidence/attach")
async def attach_evidence(file: UploadFile = File(...)):
    """
    Attach a new evidence document.
    
    For the hackathon demo, this just returns success.
    In production, this would:
    1. Save the file
    2. Process and chunk it
    3. Assign excerpt IDs
    4. Add to the retriever
    """
    content = await file.read()
    
    return {
        "status": "success",
        "message": f"Evidence file '{file.filename}' attached",
        "size_bytes": len(content),
        "note": "Use include_acceptance_email=true in /api/judge to include acceptance evidence"
    }


@app.get("/api/traces", response_model=TraceListResponse)
async def list_traces(limit: int = 50):
    """List recent judgment traces."""
    orchestrator = await _get_orchestrator()
    traces = await orchestrator.trace_store.list_traces(limit=limit)
    
    return TraceListResponse(
        traces=[t.model_dump() for t in traces],
        count=len(traces),
    )


@app.get("/api/traces/{run_id}")
async def get_trace(run_id: str):
    """Get a specific trace by run ID."""
    orchestrator = await _get_orchestrator()
    trace = await orchestrator.trace_store.get_trace(run_id)
    
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found")
    
    return trace.model_dump()


@app.get("/api/excerpts")
async def list_excerpts(include_acceptance: bool = False):
    """List available excerpts."""
    retriever = _get_retriever(include_acceptance=include_acceptance)
    
    excerpts = {}
    for doc_type, excerpt_list in retriever.excerpts_by_type.items():
        excerpts[doc_type] = [
            {
                "excerpt_id": e.excerpt_id,
                "cite_token": e.cite_token,
                "doc_id": e.doc_id,
                "text_preview": e.text[:200] + "..." if len(e.text) > 200 else e.text
            }
            for e in excerpt_list
        ]
    
    return {"excerpts": excerpts}


@app.get("/api/demo/scenarios")
async def get_demo_scenarios():
    """Get the demo scenarios for testing."""
    return {
        "scenarios": [
            {
                "name": "Scenario A: Missing Acceptance",
                "question": "Can we recognize ₹12Cr revenue this quarter for Customer K?",
                "include_acceptance_email": False,
                "expected_verdict": "INSUFFICIENT_EVIDENCE",
                "description": "Without acceptance email, Evidence Agent should report MISSING"
            },
            {
                "name": "Scenario B: With Acceptance",
                "question": "Can we recognize ₹12Cr revenue this quarter for Customer K?",
                "include_acceptance_email": True,
                "expected_verdict": "APPROVE",
                "description": "With acceptance email, verdict should flip to APPROVE"
            },
            {
                "name": "Scenario C: Hard-Stop (same question, but Risk Agent should flag termination clause)",
                "question": "Can we recognize ₹12Cr revenue this quarter for Customer K?",
                "include_acceptance_email": False,
                "expected_verdict": "INSUFFICIENT_EVIDENCE or REJECT",
                "description": "Risk Agent may flag the 30-day termination clause as a hard-stop"
            }
        ]
    }
