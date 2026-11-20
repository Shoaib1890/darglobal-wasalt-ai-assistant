import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# RAG & Storage Configuration
CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR", 
    str(BASE_DIR / "data" / "chroma_db")
)
RAG_CHUNKS_PATH = os.getenv(
    "RAG_CHUNKS_PATH", 
    str(BASE_DIR / "data" / "processed" / "rag_chunks.json")
)
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", 
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Retrieval Defaults
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "4"))
SIMILARITY_RELEVANCE_THRESHOLD = float(os.getenv("SIMILARITY_RELEVANCE_THRESHOLD", "0.35"))

# App Info
APP_NAME = "DarGlobal & Wasalt AI Assistant API"
APP_VERSION = "1.0.0"
