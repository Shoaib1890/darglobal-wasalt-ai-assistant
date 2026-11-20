import re
import logging
from typing import List, Dict, Any, Optional
from backend.rag.vector_store import vector_store
from backend.config import DEFAULT_TOP_K, SIMILARITY_RELEVANCE_THRESHOLD

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Combines semantic vector similarity with exact keyword matching for accurate retrieval."""

    def __init__(self):
        self.vs = vector_store

    def _keyword_boost(self, query: str, text: str, section: str = "") -> float:
        """Calculates a lexical match score for domain-specific acronyms and entities."""
        query_tokens = set(re.findall(r'[\w\u0600-\u06FF]+', query.lower()))
        if not query_tokens:
            return 0.0

        # Exact keywords of high significance
        priority_terms = {
            "rega", "الهيئة", "العقار", "1200016591", "مزادات", "وصلت", "ترخيص",
            "naiza", "dar u", "darlean", "dossym", "tns", "tns+", "qazcode",
            "утемуратов", "utemuratov", "veon", "казахстан", "kazakhstan",
            "education", "university", "sports", "sport", "telecom", "projects", "ecosystem"
        }
        
        matches = 0
        priority_matches = 0
        text_lower = f"{text} {section}".lower()
        
        for token in query_tokens:
            if len(token) > 2 and token in text_lower:
                matches += 1
                if token in priority_terms:
                    priority_matches += 1

        boost = (matches * 0.05) + (priority_matches * 0.15)
        return min(0.35, boost)

    def retrieve(
        self, 
        query: str, 
        top_k: int = DEFAULT_TOP_K, 
        domain_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves and ranks chunks using combined dense semantic and lexical relevance."""
        # Retrieve more candidates from ChromaDB for re-ranking
        candidates = self.vs.query(
            query_text=query,
            n_results=min(12, max(top_k * 2, 6)),
            domain_filter=domain_filter
        )

        ranked = []
        for item in candidates:
            semantic_score = item["score"]
            boost = self._keyword_boost(query, item["text"], item.get("section", ""))
            hybrid_score = min(1.0, semantic_score + boost)
            
            item["score"] = round(hybrid_score, 4)
            ranked.append(item)

        # Sort descending by hybrid score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        top_results = ranked[:top_k]

        return top_results

retriever = HybridRetriever()
