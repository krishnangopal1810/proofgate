"""
Unit Tests for Retrieval

Tests for the SimpleRetriever module.
"""

import pytest

from src.retrieve.simple import SimpleRetriever
from src.schemas.documents import ExcerptBlock


class TestSimpleRetriever:
    """Tests for SimpleRetriever."""
    
    @pytest.fixture
    def sample_excerpts(self):
        """Create sample excerpts for testing."""
        return {
            'policy': [
                ExcerptBlock.create("POL-001", "policy1", "policy", "Policy excerpt 1"),
                ExcerptBlock.create("POL-002", "policy1", "policy", "Policy excerpt 2"),
                ExcerptBlock.create("POL-003", "policy1", "policy", "Policy excerpt 3"),
            ],
            'contract': [
                ExcerptBlock.create("CON-001", "contract1", "contract", "Contract excerpt 1"),
                ExcerptBlock.create("CON-002", "contract1", "contract", "Contract excerpt 2"),
            ],
            'evidence': [
                ExcerptBlock.create("EVI-001", "evidence1", "evidence", "Evidence excerpt 1"),
                ExcerptBlock.create("EVI-002", "evidence2", "evidence", "Evidence excerpt 2"),
                ExcerptBlock.create("EVI-003", "evidence3", "evidence", "Evidence excerpt 3"),
            ],
        }
    
    def test_retrieve_default_limits(self, sample_excerpts):
        """Test retrieval with default limits (2 each)."""
        retriever = SimpleRetriever(sample_excerpts)
        result = retriever.retrieve("Any question")
        
        assert len(result['policy']) == 2
        assert len(result['contract']) == 2
        assert len(result['evidence']) == 2
    
    def test_retrieve_custom_limits(self, sample_excerpts):
        """Test retrieval with custom limits."""
        retriever = SimpleRetriever(
            sample_excerpts,
            policy_limit=1,
            contract_limit=2,
            evidence_limit=3,
        )
        result = retriever.retrieve("Any question")
        
        assert len(result['policy']) == 1
        assert len(result['contract']) == 2
        assert len(result['evidence']) == 3
    
    def test_retrieve_respects_available_count(self, sample_excerpts):
        """Test that retrieval doesn't exceed available excerpts."""
        retriever = SimpleRetriever(
            sample_excerpts,
            policy_limit=10,  # More than available
        )
        result = retriever.retrieve("Any question")
        
        # Should only get 3 (what's available)
        assert len(result['policy']) == 3
    
    def test_retrieve_flat(self, sample_excerpts):
        """Test flat retrieval returns all excerpts."""
        retriever = SimpleRetriever(sample_excerpts)
        flat_result = retriever.retrieve_flat("Any question")
        
        # 2 + 2 + 2 = 6 (default limits)
        assert len(flat_result) == 6
    
    def test_get_allowed_citations(self, sample_excerpts):
        """Test getting allowed citation set."""
        retriever = SimpleRetriever(sample_excerpts)
        allowed = retriever.get_allowed_citations("Any question")
        
        assert len(allowed) == 6
        assert "POL-001" in allowed
        assert "POL-002" in allowed
        assert "CON-001" in allowed
        assert "CON-002" in allowed
        assert "EVI-001" in allowed
        assert "EVI-002" in allowed
        # POL-003 and EVI-003 should NOT be included (limit=2)
        assert "POL-003" not in allowed
        assert "EVI-003" not in allowed
    
    def test_format_excerpts_for_prompt(self, sample_excerpts):
        """Test formatting excerpts for agent prompts."""
        retriever = SimpleRetriever(sample_excerpts)
        formatted = retriever.format_excerpts_for_prompt("Any question")
        
        assert 'policy' in formatted
        assert 'contract' in formatted
        assert 'evidence' in formatted
        
        # Check cite tokens are included
        assert "[CITE=POL-001]" in formatted['policy']
        assert "[CITE=CON-001]" in formatted['contract']
        assert "[CITE=EVI-001]" in formatted['evidence']
    
    def test_empty_excerpts_handled(self):
        """Test handling of empty excerpt categories."""
        excerpts = {
            'policy': [],
            'contract': [],
            'evidence': [],
        }
        retriever = SimpleRetriever(excerpts)
        result = retriever.retrieve("Any question")
        
        assert len(result['policy']) == 0
        assert len(result['contract']) == 0
        assert len(result['evidence']) == 0
    
    def test_partial_excerpts(self):
        """Test with only some categories having excerpts."""
        excerpts = {
            'policy': [
                ExcerptBlock.create("POL-001", "policy1", "policy", "Policy only"),
            ],
            'contract': [],
            'evidence': [],
        }
        retriever = SimpleRetriever(excerpts)
        result = retriever.retrieve("Any question")
        
        assert len(result['policy']) == 1
        assert len(result['contract']) == 0
        assert len(result['evidence']) == 0
