"""
Simple Retriever

For hackathon: returns first N excerpts of each type.
No ML, no embeddings, zero latency.
"""

from typing import List, Dict

from src.schemas.documents import ExcerptBlock


class SimpleRetriever:
    """
    Simple retriever that returns first N excerpts of each type.
    
    For hackathon demo - graduate to embeddings in production.
    """
    
    def __init__(
        self,
        excerpts_by_type: Dict[str, List[ExcerptBlock]],
        policy_limit: int = 2,
        contract_limit: int = 2,
        evidence_limit: int = 2,
    ):
        """
        Initialize retriever with excerpts.
        
        Args:
            excerpts_by_type: Dict mapping doc_type to list of excerpts
            policy_limit: Max policy excerpts to return
            contract_limit: Max contract excerpts to return
            evidence_limit: Max evidence excerpts to return
        """
        self.excerpts_by_type = excerpts_by_type
        self.limits = {
            'policy': policy_limit,
            'contract': contract_limit,
            'evidence': evidence_limit,
        }
    
    def retrieve(self, question: str) -> Dict[str, List[ExcerptBlock]]:
        """
        Retrieve relevant excerpts for a question.
        
        For hackathon: just returns first N of each type.
        Production: would use embeddings + similarity search.
        
        Args:
            question: The user's question (currently unused)
        
        Returns:
            Dict mapping doc_type to list of excerpts
        """
        result = {}
        
        for doc_type, excerpts in self.excerpts_by_type.items():
            limit = self.limits.get(doc_type, 2)
            result[doc_type] = excerpts[:limit]
        
        return result
    
    def retrieve_flat(self, question: str) -> List[ExcerptBlock]:
        """Return all retrieved excerpts as a flat list."""
        retrieved = self.retrieve(question)
        return [
            excerpt
            for excerpts in retrieved.values()
            for excerpt in excerpts
        ]
    
    def get_allowed_citations(self, question: str) -> set:
        """Get the set of allowed citation IDs for a question."""
        excerpts = self.retrieve_flat(question)
        return {e.excerpt_id for e in excerpts}
    
    def format_excerpts_for_prompt(self, question: str) -> Dict[str, str]:
        """
        Format retrieved excerpts as text for agent prompts.
        
        Returns:
            Dict with formatted text for each doc type
        """
        retrieved = self.retrieve(question)
        formatted = {}
        
        for doc_type, excerpts in retrieved.items():
            if excerpts:
                text_parts = []
                for excerpt in excerpts:
                    text_parts.append(
                        f"{excerpt.cite_token}\n{excerpt.text}"
                    )
                formatted[doc_type] = "\n\n---\n\n".join(text_parts)
            else:
                formatted[doc_type] = "(No excerpts available)"
        
        return formatted
