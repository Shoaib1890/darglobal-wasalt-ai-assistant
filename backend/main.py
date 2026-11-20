import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.api.routes import router as api_router
from backend.config import APP_NAME, APP_VERSION
from backend.rag.vector_store import vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure ChromaDB vector store is ready
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}...")
    count = vector_store.get_count()
    logger.info(f"Vector store initialized with {count} verified chunks.")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Production-grade AI chatbot backend for DarGlobal and Wasalt knowledge bases.",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Mount static frontend files if directory exists (for unified Docker deployment in Phase 4)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    logger.info(f"Listening on http://0.0.0.0:{port}")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
