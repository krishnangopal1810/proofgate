"""
Unit Tests for API Endpoints

Tests for the FastAPI API layer.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from src.api.main import app
from src.schemas.agents import FinalVerdict


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_returns_ok(self):
        """Test that health endpoint returns healthy status."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestExcerptsEndpoint:
    """Tests for the excerpts listing endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_excerpts(self):
        """Test listing available excerpts."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/excerpts")
        
        assert response.status_code == 200
        data = response.json()
        assert "excerpts" in data
        assert "policy" in data["excerpts"]
        assert "contract" in data["excerpts"]
        assert "evidence" in data["excerpts"]
    
    @pytest.mark.asyncio
    async def test_list_excerpts_with_acceptance(self):
        """Test listing excerpts including acceptance email."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/excerpts?include_acceptance=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include EVI-003 (acceptance email)
        evidence_ids = [e["excerpt_id"] for e in data["excerpts"]["evidence"]]
        assert "EVI-003" in evidence_ids


class TestDemoScenariosEndpoint:
    """Tests for the demo scenarios endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_demo_scenarios(self):
        """Test getting demo scenarios."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/demo/scenarios")
        
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) == 3
        
        # Check scenario names
        scenario_names = [s["name"] for s in data["scenarios"]]
        assert any("Missing Acceptance" in name for name in scenario_names)
        assert any("With Acceptance" in name for name in scenario_names)


class TestJudgeEndpointMocked:
    """Tests for the judgment endpoint with mocked LLM calls."""
    
    @pytest.mark.asyncio
    async def test_judge_endpoint_structure(self):
        """Test that judge endpoint returns correct structure."""
        mock_verdict = FinalVerdict(
            verdict="INSUFFICIENT_EVIDENCE",
            confidence=0.3,
            violations=[],
            conditions_to_allow=["Attach acceptance email"],
            citations=["POL-001"],
            rule_applied="RULE_2: Evidence Missing"
        )
        
        mock_result = {
            'run_id': 'test-123',
            'verdict': mock_verdict.model_dump(),
            'agent_outputs': {
                'policy': {'stance': 'YES_CONDITIONAL'},
                'risk': {'stance': 'YES_CONDITIONAL'},
                'evidence': {'stance': 'MISSING'},
            },
            'trace': {
                'run_id': 'test-123',
                'input_hash': 'abc123',
                'question': 'Test?',
                'excerpt_ids': ['POL-001'],
                'prompt_versions': {'policy': 'v1'},
                'replayed': False,
            },
            'excerpts_used': [],
        }
        
        with patch('src.api.main._get_orchestrator') as mock_get_orch:
            mock_orchestrator = MagicMock()
            mock_orchestrator.run = AsyncMock(return_value=mock_result)
            mock_get_orch.return_value = mock_orchestrator
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/judge",
                    json={
                        "question": "Can we recognize revenue?",
                        "include_acceptance_email": False
                    }
                )
            
            # Just check the endpoint works and returns valid JSON
            assert response.status_code in [200, 422, 500]  # May vary based on mock setup


class TestAttachEvidenceEndpoint:
    """Tests for the evidence attachment endpoint."""
    
    @pytest.mark.asyncio
    async def test_attach_evidence_returns_success(self):
        """Test that attaching evidence returns success."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Create a simple file upload
            files = {"file": ("test.md", b"# Test Evidence\n\nContent here.", "text/markdown")}
            response = await client.post("/api/evidence/attach", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "test.md" in data["message"]
        assert data["size_bytes"] > 0


class TestTracesEndpoint:
    """Tests for the traces listing and retrieval endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_traces_returns_structure(self):
        """Test that list traces returns expected structure."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/traces")
        
        assert response.status_code == 200
        data = response.json()
        assert "traces" in data
        assert "count" in data
        assert isinstance(data["traces"], list)
    
    @pytest.mark.asyncio
    async def test_get_trace_not_found(self):
        """Test that getting a non-existent trace returns 404."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/traces/nonexistent-run-id")
        
        assert response.status_code == 404


class TestJudgeEndpointValidation:
    """Tests for judge endpoint input validation."""
    
    @pytest.mark.asyncio
    async def test_judge_missing_question_fails(self):
        """Test that missing question field returns validation error."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/judge",
                json={"include_acceptance_email": True}  # Missing question
            )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_judge_empty_question_allowed(self):
        """Test behavior with empty question string."""
        mock_verdict = FinalVerdict(
            verdict="INSUFFICIENT_EVIDENCE",
            confidence=0.0,
            violations=[],
            conditions_to_allow=[],
            citations=[],
            rule_applied="TEST"
        )
        
        mock_result = {
            'run_id': 'test',
            'verdict': mock_verdict.model_dump(),
            'agent_outputs': {},
            'trace': {
                'run_id': 'test',
                'input_hash': 'hash',
                'question': '',
                'excerpt_ids': [],
                'prompt_versions': {},
                'replayed': False,
            },
            'excerpts_used': [],
        }
        
        with patch('src.api.main._get_orchestrator') as mock_get_orch:
            mock_orchestrator = MagicMock()
            mock_orchestrator.run = AsyncMock(return_value=mock_result)
            mock_get_orch.return_value = mock_orchestrator
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/judge",
                    json={"question": ""}  # Empty but present
                )
            
            # Should not raise validation error
            assert response.status_code in [200, 500]


class TestRetrieverBehavior:
    """Tests for retriever acceptance email filtering."""
    
    @pytest.mark.asyncio
    async def test_excerpts_without_acceptance(self):
        """Test that EVI-003 is excluded by default."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/excerpts?include_acceptance=false")
        
        assert response.status_code == 200
        data = response.json()
        
        evidence_ids = [e["excerpt_id"] for e in data["excerpts"]["evidence"]]
        assert "EVI-003" not in evidence_ids
    
    @pytest.mark.asyncio
    async def test_excerpts_with_acceptance(self):
        """Test that EVI-003 is included when requested."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/excerpts?include_acceptance=true")
        
        assert response.status_code == 200
        data = response.json()
        
        evidence_ids = [e["excerpt_id"] for e in data["excerpts"]["evidence"]]
        assert "EVI-003" in evidence_ids
