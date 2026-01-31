"""
ProofGate API Package

FastAPI endpoints for the ProofGate service.
"""

from .main import app, create_app

__all__ = ["app", "create_app"]
