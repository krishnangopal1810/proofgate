"""
Citation Whitelist Guard

Ensures agents ONLY cite excerpts that were provided.
Any hallucinated citation triggers a retry or failure.
"""

from typing import List, Tuple, Set, Any
from pydantic import BaseModel


class CitationValidationError(Exception):
    """Raised when an agent produces hallucinated citations."""
    
    def __init__(self, hallucinated: List[str], allowed: Set[str]):
        self.hallucinated = hallucinated
        self.allowed = allowed
        super().__init__(
            f"Hallucinated citations detected: {hallucinated}. "
            f"Allowed citations: {sorted(allowed)}"
        )


def validate_citations(
    output: BaseModel,
    allowed_citations: Set[str],
    raise_on_error: bool = False
) -> Tuple[bool, List[str]]:
    """
    Validate that all citations in an agent output are in the whitelist.
    
    Args:
        output: Pydantic model with a 'citations' field
        allowed_citations: Set of allowed excerpt IDs
        raise_on_error: If True, raise CitationValidationError on invalid citations
    
    Returns:
        Tuple of (is_valid, list_of_hallucinated_citations)
    
    Raises:
        CitationValidationError: If raise_on_error=True and invalid citations found
    """
    # Extract citations from output
    citations = getattr(output, 'citations', []) or []
    
    # Find any citations not in the whitelist
    output_citations = set(citations)
    hallucinated = output_citations - allowed_citations
    
    is_valid = len(hallucinated) == 0
    hallucinated_list = sorted(list(hallucinated))
    
    if not is_valid and raise_on_error:
        raise CitationValidationError(hallucinated_list, allowed_citations)
    
    return is_valid, hallucinated_list


def validate_all_agent_outputs(
    outputs: dict,
    allowed_citations: Set[str]
) -> dict:
    """
    Validate citations for multiple agent outputs.
    
    Args:
        outputs: Dict mapping agent name to output
        allowed_citations: Set of allowed excerpt IDs
    
    Returns:
        Dict with validation results per agent
    """
    results = {}
    
    for agent_name, output in outputs.items():
        is_valid, hallucinated = validate_citations(output, allowed_citations)
        results[agent_name] = {
            'is_valid': is_valid,
            'hallucinated': hallucinated,
        }
    
    return results


def get_all_citations_from_outputs(outputs: dict) -> Set[str]:
    """Extract all citations from multiple agent outputs."""
    all_citations = set()
    
    for output in outputs.values():
        citations = getattr(output, 'citations', []) or []
        all_citations.update(citations)
    
    return all_citations
