"""
Unit Tests for Document Ingestion

Tests for loading and parsing documents with excerpt IDs.
"""

import pytest
from pathlib import Path
import tempfile
import os

from src.ingest.loader import (
    load_document,
    parse_excerpts_from_document,
    load_all_documents,
)
from src.schemas.documents import Document


class TestLoadDocument:
    """Tests for document loading."""
    
    def test_load_markdown_document(self):
        """Test loading a markdown document."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write("# Test Policy\n\nThis is the content.")
            f.flush()
            
            try:
                doc = load_document(Path(f.name), doc_type="policy")
                assert doc.doc_type == "policy"
                assert doc.title == "Test Policy"
                assert "This is the content" in doc.content
            finally:
                os.unlink(f.name)
    
    def test_document_hash_computed(self):
        """Test that content hash is computed on load."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write("# Doc\n\nContent here.")
            f.flush()
            
            try:
                doc = load_document(Path(f.name), doc_type="evidence")
                assert doc.content_hash != ""
                assert len(doc.content_hash) == 64
            finally:
                os.unlink(f.name)
    
    def test_explicit_doc_id(self):
        """Test setting explicit document ID."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        ) as f:
            f.write("Content")
            f.flush()
            
            try:
                doc = load_document(
                    Path(f.name), 
                    doc_type="policy",
                    doc_id="custom_id"
                )
                assert doc.doc_id == "custom_id"
            finally:
                os.unlink(f.name)


class TestParseExcerpts:
    """Tests for excerpt parsing from documents."""
    
    def test_parse_single_excerpt(self):
        """Test parsing a single excerpt."""
        doc = Document(
            doc_id="test",
            doc_type="policy",
            title="Test",
            content="[CITE=POL-001]\nThis is the excerpt content.\n---"
        )
        
        excerpts = parse_excerpts_from_document(doc)
        
        assert len(excerpts) == 1
        assert excerpts[0].excerpt_id == "POL-001"
        assert excerpts[0].cite_token == "[CITE=POL-001]"
        assert "This is the excerpt content" in excerpts[0].text
    
    def test_parse_multiple_excerpts(self):
        """Test parsing multiple excerpts."""
        doc = Document(
            doc_id="test",
            doc_type="policy",
            title="Test",
            content="""
[CITE=POL-001]
First excerpt content.

---

[CITE=POL-002]
Second excerpt content.

---

[CITE=POL-003]
Third excerpt content.
"""
        )
        
        excerpts = parse_excerpts_from_document(doc)
        
        assert len(excerpts) == 3
        assert excerpts[0].excerpt_id == "POL-001"
        assert excerpts[1].excerpt_id == "POL-002"
        assert excerpts[2].excerpt_id == "POL-003"
    
    def test_excerpts_inherit_doc_type(self):
        """Test that excerpts inherit document type."""
        doc = Document(
            doc_id="contract",
            doc_type="contract",
            title="Contract",
            content="[CITE=CON-001]\nContract clause."
        )
        
        excerpts = parse_excerpts_from_document(doc)
        
        assert excerpts[0].doc_type == "contract"
    
    def test_no_excerpts_returns_empty(self):
        """Test document with no cite tokens returns empty list."""
        doc = Document(
            doc_id="test",
            doc_type="policy",
            title="Test",
            content="No cite tokens in this document."
        )
        
        excerpts = parse_excerpts_from_document(doc)
        
        assert len(excerpts) == 0
    
    def test_excerpt_id_format_validated(self):
        """Test that only valid excerpt IDs are parsed."""
        doc = Document(
            doc_id="test",
            doc_type="policy",
            title="Test",
            content="""
[CITE=POL-001]
Valid excerpt.

[CITE=INVALID]
This should not be parsed.

[CITE=EVI-123]
Another valid excerpt.
"""
        )
        
        excerpts = parse_excerpts_from_document(doc)
        
        # Only POL-001 and EVI-123 should be parsed (3 uppercase + dash + 3 digits)
        excerpt_ids = [e.excerpt_id for e in excerpts]
        assert "POL-001" in excerpt_ids
        assert "EVI-123" in excerpt_ids
        # INVALID doesn't match XXX-### pattern
        assert "INVALID" not in excerpt_ids


class TestLoadAllDocuments:
    """Tests for loading all documents from directory."""
    
    def test_load_from_data_directory(self):
        """Test loading from actual data directory."""
        data_dir = Path(__file__).parent.parent / "data"
        
        if not data_dir.exists():
            pytest.skip("Data directory not found")
        
        result = load_all_documents(data_dir)
        
        assert 'documents' in result
        assert 'excerpts' in result
        assert 'all_excerpts' in result
        
        # Should have excerpts by type
        assert 'policy' in result['excerpts']
        assert 'contract' in result['excerpts']
        assert 'evidence' in result['excerpts']
    
    def test_excerpts_have_correct_format(self):
        """Test that loaded excerpts have correct cite tokens."""
        data_dir = Path(__file__).parent.parent / "data"
        
        if not data_dir.exists():
            pytest.skip("Data directory not found")
        
        result = load_all_documents(data_dir)
        
        for excerpt in result['all_excerpts']:
            # Verify cite token format
            assert excerpt.cite_token.startswith("[CITE=")
            assert excerpt.cite_token.endswith("]")
            # Verify excerpt ID matches cite token
            assert excerpt.excerpt_id in excerpt.cite_token
