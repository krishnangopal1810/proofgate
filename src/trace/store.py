"""
Trace Store

SQLite-based storage for run traces and deterministic replay caching.
"""

import json
import hashlib
import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from src.schemas.documents import RunTrace


class TraceStore:
    """
    SQLite-based trace storage for auditability and replay.
    
    Enables:
    - Deterministic replay: same inputs → same outputs
    - Audit trail: every run is logged with hashes
    - Caching: skip re-computation for identical inputs
    """
    
    def __init__(self, db_path: Path = None):
        """
        Initialize trace store.
        
        Args:
            db_path: Path to SQLite database (defaults to ./data/traces.db)
        """
        self.db_path = db_path or Path("./data/traces.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def init_db(self):
        """Create tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    run_id TEXT PRIMARY KEY,
                    input_hash TEXT NOT NULL,
                    question TEXT NOT NULL,
                    excerpt_ids TEXT NOT NULL,
                    prompt_versions TEXT NOT NULL,
                    agent_output_hashes TEXT,
                    final_output_hash TEXT,
                    result_json TEXT,
                    replayed INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL,
                    latency_ms INTEGER
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_input_hash 
                ON traces(input_hash)
            """)
            await db.commit()
    
    @staticmethod
    def compute_input_hash(
        question: str,
        excerpt_ids: List[str],
        prompt_versions: Dict[str, str]
    ) -> str:
        """
        Compute deterministic hash for caching/replay.
        
        Same inputs will always produce the same hash.
        """
        sorted_excerpts = ",".join(sorted(excerpt_ids))
        sorted_prompts = ",".join(
            f"{k}:{v}" for k, v in sorted(prompt_versions.items())
        )
        payload = f"{question}|{sorted_excerpts}|{sorted_prompts}"
        return hashlib.sha256(payload.encode()).hexdigest()
    
    @staticmethod
    def compute_output_hash(output: Any) -> str:
        """Compute hash of an output for verification."""
        if isinstance(output, BaseModel):
            # Pydantic v2: use model_dump then json.dumps for sorting
            content = json.dumps(output.model_dump(), sort_keys=True)
        else:
            content = json.dumps(output, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get_cached_result(
        self, 
        input_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if we have a cached result for this input hash.
        
        Returns:
            Cached result dict if found, None otherwise
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT result_json FROM traces WHERE input_hash = ?",
                (input_hash,)
            ) as cursor:
                row = await cursor.fetchone()
                if row and row['result_json']:
                    return json.loads(row['result_json'])
        return None
    
    async def store_trace(
        self,
        trace: RunTrace,
        result: Dict[str, Any] = None
    ) -> None:
        """
        Store a run trace.
        
        Args:
            trace: The RunTrace object
            result: Optional full result dict to cache
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO traces 
                (run_id, input_hash, question, excerpt_ids, prompt_versions,
                 agent_output_hashes, final_output_hash, result_json, 
                 replayed, timestamp, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trace.run_id,
                trace.input_hash,
                trace.question,
                json.dumps(trace.excerpt_ids),
                json.dumps(trace.prompt_versions),
                json.dumps(trace.agent_output_hashes),
                trace.final_output_hash,
                json.dumps(result) if result else None,
                1 if trace.replayed else 0,
                trace.timestamp or datetime.now(tz=None).isoformat(),
                trace.latency_ms,
            ))
            await db.commit()
    
    async def get_trace(self, run_id: str) -> Optional[RunTrace]:
        """Get a trace by run ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM traces WHERE run_id = ?",
                (run_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return RunTrace(
                        run_id=row['run_id'],
                        input_hash=row['input_hash'],
                        question=row['question'],
                        excerpt_ids=json.loads(row['excerpt_ids']),
                        prompt_versions=json.loads(row['prompt_versions']),
                        agent_output_hashes=json.loads(
                            row['agent_output_hashes'] or '{}'
                        ),
                        final_output_hash=row['final_output_hash'] or '',
                        replayed=bool(row['replayed']),
                        timestamp=row['timestamp'],
                        latency_ms=row['latency_ms'],
                    )
        return None
    
    async def list_traces(
        self, 
        limit: int = 50
    ) -> List[RunTrace]:
        """List recent traces."""
        traces = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM traces ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ) as cursor:
                async for row in cursor:
                    traces.append(RunTrace(
                        run_id=row['run_id'],
                        input_hash=row['input_hash'],
                        question=row['question'],
                        excerpt_ids=json.loads(row['excerpt_ids']),
                        prompt_versions=json.loads(row['prompt_versions']),
                        agent_output_hashes=json.loads(
                            row['agent_output_hashes'] or '{}'
                        ),
                        final_output_hash=row['final_output_hash'] or '',
                        replayed=bool(row['replayed']),
                        timestamp=row['timestamp'],
                        latency_ms=row['latency_ms'],
                    ))
        return traces
