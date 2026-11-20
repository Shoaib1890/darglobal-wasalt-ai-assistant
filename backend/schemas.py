from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    domain: str
    source_url: str
    page_title: str
    section: str
    language: str
    text: str
    score: float = Field(..., description="Relevance score (higher is more relevant)")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    top_k: int = Field(default=4, ge=1, le=10, description="Number of chunks to return")
    domain_filter: Optional[str] = Field(default=None, description="Filter by domain: 'darglobal.com' or 'wasalt.sa'")

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., min_length=1, description="Message text")

class Citation(BaseModel):
    chunk_id: str
    domain: str
    source_url: str
    section: str
    quote: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question or prompt")
    history: List[ChatMessage] = Field(default_factory=list, description="Conversation history")
    top_k: int = Field(default=4, ge=1, le=8, description="Number of context chunks to retrieve")

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    grounded: bool
    model_used: str

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    vector_store_ready: bool
    total_chunks: int
    openrouter_configured: bool
    model_name: str
