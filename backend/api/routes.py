import logging
from fastapi import APIRouter, HTTPException, Depends
from backend.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    ChatRequest,
    ChatResponse,
    HealthResponse
)
from backend.rag.retriever import retriever
from backend.rag.vector_store import vector_store
from backend.rag.openrouter_client import openrouter_client
from backend.config import APP_NAME, APP_VERSION, OPENROUTER_MODEL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["AI Assistant"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Returns application health, ChromaDB chunk count, and model configuration."""
    chunk_count = vector_store.get_count()
    return HealthResponse(
        status="healthy",
        app_name=APP_NAME,
        version=APP_VERSION,
        vector_store_ready=chunk_count > 0,
        total_chunks=chunk_count,
        openrouter_configured=openrouter_client.is_configured(),
        model_name=OPENROUTER_MODEL
    )

@router.post("/search", response_model=SearchResponse)
async def search_knowledge(req: SearchRequest):
    """
    Direct semantic & lexical hybrid retrieval against the verified knowledge base.
    Returns ranked chunks with relevance scores and source attribution.
    """
    try:
        results = retriever.retrieve(
            query=req.query,
            top_k=req.top_k,
            domain_filter=req.domain_filter
        )
        search_results = [SearchResult(**r) for r in results]
        return SearchResponse(
            query=req.query,
            results=search_results,
            total_found=len(search_results)
        )
    except Exception as e:
        logger.error(f"Search endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search retrieval error: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Grounded question-answering endpoint.
    Retrieves verified chunks, constructs anti-hallucination context, and generates
    bilingual answers with structured source citations.
    """
    try:
        # 1. Retrieve top context chunks
        chunks = retriever.retrieve(
            query=req.message,
            top_k=req.top_k
        )
        
        # 2. Generate response via OpenRouter (or grounded fallback if no key)
        answer, citations, grounded, model_used = await openrouter_client.generate_response(
            query=req.message,
            retrieved_chunks=chunks,
            history=req.history
        )

        return ChatResponse(
            answer=answer,
            citations=citations,
            grounded=grounded,
            model_used=model_used
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat generation error: {str(e)}")
