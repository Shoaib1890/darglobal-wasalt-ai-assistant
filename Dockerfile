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

# Set environment variables for ultra-low memory footprint
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight Python requirements (Zero PyTorch, <110MB RAM)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set up user for compatibility with rootless container runtimes (uid 1000)
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
USER user

# Expose ports for Render (10000) and Hugging Face (7860)
EXPOSE 10000 7860

# Launch Uvicorn bound to 0.0.0.0 on Render / Hugging Face dynamic PORT
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
