# ==========================================
# Stage 1: Build the React TypeScript Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy source code and build production bundle
COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Python Backend & Runtime Service
# ==========================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download multilingual embedding model to warm container cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Set up user for Hugging Face Spaces compatibility (uid 1000)
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Copy project files
COPY backend/ ./backend/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Copy compiled frontend from Stage 1 into backend static directory
COPY --from=frontend-builder /app/backend/static ./backend/static

# Ensure correct permissions for persistent ChromaDB storage
RUN mkdir -p /app/data/chroma_db && chown -R user:user /app

# Switch to non-root user
USER user

# Expose standard port for Hugging Face Spaces / Container platforms
EXPOSE 7860

# Launch Uvicorn server bound to 0.0.0.0 with dynamic PORT fallback
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
