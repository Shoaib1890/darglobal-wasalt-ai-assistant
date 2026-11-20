import logging
import re
from typing import List, Dict, Any, Tuple
import httpx
from backend.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_BASE_URL,
    SIMILARITY_RELEVANCE_THRESHOLD
)
from backend.prompt import build_prompt_with_context
from backend.schemas import Citation, ChatMessage

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.base_url = OPENROUTER_BASE_URL

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        history: List[ChatMessage] = None
    ) -> Tuple[str, List[Citation], bool, str]:
        """
        Sends grounded query to OpenRouter LLM.
        Returns: (answer, citations, is_grounded, model_name)
        """
        # 1. Guardrail: Check if the retrieved context has sufficient relevance
        # If top score is below threshold, reject without calling LLM to prevent hallucination
        is_relevant = bool(
            retrieved_chunks and 
            any(c["score"] >= SIMILARITY_RELEVANCE_THRESHOLD for c in retrieved_chunks)
        )

        # Detect Arabic query
        is_arabic = bool(re.search(r'[\u0600-\u06FF]', query))

        if not is_relevant:
            if is_arabic:
                refusal_msg = (
                    "هذه المعلومة غير متوفرة ضمن المحتوى المعتمد من منصتي darglobal.com وwasalt.sa. "
                    "يمكنني فقط الإجابة عن مشاريع مجموعة DAR الرقمية (مثل Naiza، DAR U، Darlean، TNS+) "
                    "وخدمات وتراخيص منصة وصلت العقارية في السعودية."
                )
            else:
                refusal_msg = (
                    "This information is not available in the verified knowledge base from darglobal.com and wasalt.sa. "
                    "I can only assist with verified topics concerning DAR Ecosystem projects (e.g. Naiza, DAR U, Darlean, TNS+) "
                    "and Wasalt Saudi real estate services and official licensing."
                )
            return refusal_msg, [], False, self.model

        # 2. Check if OpenRouter API Key is configured
        if not self.is_configured():
            logger.info("OPENROUTER_API_KEY is not configured. Returning grounded retrieved facts.")
            # Synthesize factual response directly from top chunk
            top_chunk = retrieved_chunks[0]
            if is_arabic:
                ans = (
                    f"تم استرجاع البيانات التالية من منصة {top_chunk['domain']} (قسم: {top_chunk['section']}):\n\n"
                    f"{top_chunk['text']}\n\n"
                    "*(ملاحظة: لتفعيل صياغة الإجابات الذكية عبر LLM، يُرجى تزويد مفتاح OPENROUTER_API_KEY)*"
                )
            else:
                ans = (
                    f"Verified information retrieved from {top_chunk['domain']} (Section: {top_chunk['section']}):\n\n"
                    f"{top_chunk['text']}\n\n"
                    "*(Note: To enable generative LLM inference, configure OPENROUTER_API_KEY in your environment)*"
                )
            citation = Citation(
                chunk_id=top_chunk["chunk_id"],
                domain=top_chunk["domain"],
                source_url=top_chunk["source_url"],
                section=top_chunk["section"],
                quote=top_chunk["text"][:200] + "..."
            )
            return ans, [citation], True, "grounded-retriever-fallback"

        # 3. Call OpenRouter API with multi-model fallback chain to defeat rate limits
        candidate_models = [
            self.model,
            "google/gemma-4-31b-it:free",
            "google/gemma-4-26b-a4b-it:free",
            "nvidia/nemotron-3.5-lightning:free",
            "openrouter/free"
        ]
        # Deduplicate preserving order
        models_to_try = list(dict.fromkeys(candidate_models))

        messages = build_prompt_with_context(query, retrieved_chunks, history)
        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://darglobal-wasalt-assistant.local",
            "X-Title": "DarGlobal & Wasalt AI Assistant"
        }

        async with httpx.AsyncClient(timeout=35.0) as client:
            for model_candidate in models_to_try:
                payload = {
                    "model": model_candidate,
                    "messages": messages,
                    "temperature": 0.1,  # Strictly factual
                    "max_tokens": 1000
                }
                try:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        answer = data["choices"][0]["message"]["content"]
                        model_used = data.get("model", model_candidate)

                        # Extract citations
                        citations = []
                        for chunk in retrieved_chunks:
                            if chunk["chunk_id"] in answer or len(citations) < 2:
                                citations.append(Citation(
                                    chunk_id=chunk["chunk_id"],
                                    domain=chunk["domain"],
                                    source_url=chunk["source_url"],
                                    section=chunk["section"],
                                    quote=chunk["text"][:180] + "..."
                                ))

                        return answer, citations, True, model_used
                    else:
                        logger.warning(
                            f"Model {model_candidate} returned HTTP {resp.status_code} ({resp.text[:120]}). Trying next fallback model..."
                        )
                except Exception as ex:
                    logger.warning(f"Error calling {model_candidate}: {ex}. Trying next model...")

        # If all candidate models failed (e.g. general rate limit)
        top_chunk = retrieved_chunks[0]
        if is_arabic:
            fallback_text = (
                f"**المعلومات المعتمدة من منصة {top_chunk['domain']} ({top_chunk['section']}):**\n\n"
                f"{top_chunk['text']}\n\n"
                "*(ملاحظة: واجهت خدمة الذكاء الاصطناعي ضغطاً مؤقتاً، وتم تزويدكم بالبيانات الموثقة مباشرة من قاعدة المعرفة)*"
            )
        else:
            fallback_text = (
                f"**Verified Record from {top_chunk['domain']} ({top_chunk['section']}):**\n\n"
                f"{top_chunk['text']}\n\n"
                "*(Note: The free AI model queue is currently under high load; displaying the verified source data directly.)*"
            )

        citation = Citation(
            chunk_id=top_chunk["chunk_id"],
            domain=top_chunk["domain"],
            source_url=top_chunk["source_url"],
            section=top_chunk["section"],
            quote=top_chunk["text"][:200]
        )
        return fallback_text, [citation], True, "retriever-verified-record"

openrouter_client = OpenRouterClient()
