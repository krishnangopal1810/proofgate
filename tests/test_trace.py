"""
Unit Tests for Trace Store

Tests for SQLite-based trace storage and replay caching.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from src.trace.store import TraceStore
from src.schemas.documents import RunTrace
from src.schemas.agents import FinalVerdict


class TestTraceStore:
    """Tests for TraceStore."""
    
    @pytest.fixture
    async def trace_store(self):
        """Create a temporary trace store for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        
        store = TraceStore(db_path)
        await store.init_db()
        
        yield store
        
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass
    
    @pytest.mark.asyncio
    async def test_init_creates_table(self, trace_store):
        """Test that init creates the traces table."""
        import aiosqlite
        async with aiosqlite.connect(trace_store.db_path) as db:
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='traces'"
            ) as cursor:
                row = await cursor.fetchone()
                assert row is not None
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_trace(self, trace_store):
        """Test storing and retrieving a trace."""
        trace = RunTrace(
            run_id="test-123",
            input_hash="abc123",
            question="Test question?",
            excerpt_ids=["POL-001", "CON-001"],
            prompt_versions={"policy": "v1", "risk": "v1"},
            agent_output_hashes={"policy": "hash1", "risk": "hash2"},
            final_output_hash="finalhash",
            replayed=False,
            timestamp="2026-02-01T00:00:00Z",
            latency_ms=1500,
        )
        
        await trace_store.store_trace(trace)
        
        retrieved = await trace_store.get_trace("test-123")
        
        assert retrieved is not None
        assert retrieved.run_id == "test-123"
        assert retrieved.input_hash == "abc123"
        assert retrieved.question == "Test question?"
        assert "POL-001" in retrieved.excerpt_ids
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_trace(self, trace_store):
        """Test getting a trace that doesn't exist."""
        result = await trace_store.get_trace("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_result(self, trace_store):
        """Test caching and retrieving a result."""
        trace = RunTrace(
            run_id="cache-test",
            input_hash="cachehash123",
            question="Cache test?",
            excerpt_ids=["POL-001"],
            prompt_versions={"policy": "v1"},
        )
        
        result = {"verdict": "APPROVE", "confidence": 0.9}
        await trace_store.store_trace(trace, result)
        
        cached = await trace_store.get_cached_result("cachehash123")
        
        assert cached is not None
        assert cached["verdict"] == "APPROVE"
        assert cached["confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, trace_store):
        """Test cache miss for unknown hash."""
        cached = await trace_store.get_cached_result("unknownhash")
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_list_traces(self, trace_store):
        """Test listing traces."""
        # Store multiple traces
        for i in range(5):
            trace = RunTrace(
                run_id=f"run-{i}",
                input_hash=f"hash-{i}",
                question=f"Question {i}?",
                excerpt_ids=["POL-001"],
                prompt_versions={"policy": "v1"},
                timestamp=f"2026-02-01T00:0{i}:00Z",
            )
            await trace_store.store_trace(trace)
        
        traces = await trace_store.list_traces(limit=3)
        
        assert len(traces) == 3
        # Should be in reverse chronological order
        assert traces[0].run_id == "run-4"
    
    def test_compute_input_hash_deterministic(self):
        """Test that input hash is deterministic."""
        hash1 = TraceStore.compute_input_hash(
            "Question?",
            ["POL-001", "CON-001"],
            {"policy": "v1"}
        )
        hash2 = TraceStore.compute_input_hash(
            "Question?",
            ["POL-001", "CON-001"],
            {"policy": "v1"}
        )
        
        assert hash1 == hash2
    
    def test_compute_input_hash_different_for_different_inputs(self):
        """Test that different inputs produce different hashes."""
        hash1 = TraceStore.compute_input_hash(
            "Question 1?",
            ["POL-001"],
            {"policy": "v1"}
        )
        hash2 = TraceStore.compute_input_hash(
            "Question 2?",
            ["POL-001"],
            {"policy": "v1"}
        )
        
        assert hash1 != hash2
    
    def test_compute_output_hash(self):
        """Test computing output hash from Pydantic model."""
        verdict = FinalVerdict(
            verdict="APPROVE",
            confidence=0.9,
            violations=[],
            conditions_to_allow=[],
            citations=["POL-001"],
            rule_applied="RULE_5"
        )
        
        hash1 = TraceStore.compute_output_hash(verdict)
        hash2 = TraceStore.compute_output_hash(verdict)
        
        # Same output should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256
    
    @pytest.mark.asyncio
    async def test_upsert_trace(self, trace_store):
        """Test that storing with same run_id updates the trace."""
        trace1 = RunTrace(
            run_id="upsert-test",
            input_hash="hash1",
            question="Original question?",
            excerpt_ids=["POL-001"],
            prompt_versions={"policy": "v1"},
        )
        await trace_store.store_trace(trace1)
        
        # Store again with same run_id but different data
        trace2 = RunTrace(
            run_id="upsert-test",
            input_hash="hash2",  # Changed
            question="Updated question?",  # Changed
            excerpt_ids=["POL-001", "CON-001"],  # Changed
            prompt_versions={"policy": "v2"},  # Changed
        )
        await trace_store.store_trace(trace2)
        
        # Should have the updated data
        retrieved = await trace_store.get_trace("upsert-test")
        assert retrieved.input_hash == "hash2"
        assert retrieved.question == "Updated question?"
