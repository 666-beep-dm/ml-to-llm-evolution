# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools needed by some packages (faiss-cpu, numpy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Runtime system libraries needed by faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY src/ ./src/

# Volumes
# /app/data        → mount your documents here
# /app/faiss_index → persisted index (survives container restarts)
# /hf_cache        → downloaded embedding model cache
VOLUME ["/app/data", "/app/faiss_index", "/hf_cache"]

# Non-root user
RUN useradd -m appuser \
    && mkdir -p /app/data /app/faiss_index /hf_cache \
    && chown -R appuser /app /hf_cache
USER appuser

# Load .env automatically via pydantic-settings; pass it at runtime via --env-file
CMD ["python", "-u", "-m", "src.app"]
