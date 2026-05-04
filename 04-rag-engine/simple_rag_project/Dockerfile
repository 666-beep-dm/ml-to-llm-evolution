# ── Stage 1: builder ──────────────────────────────────────────────────────────
# Install dependencies in a separate stage so the final image stays lean.
FROM python:3.11-slim AS builder

WORKDIR /build

# Install deps into an isolated prefix — keeps them out of the system site-packages
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY main.py .

# Where HuggingFace will store downloaded models.
# Mount a host directory here to cache the model across container runs:
#   docker run -v $(pwd)/.hf_cache:/hf_cache ...
ENV HF_HOME=/hf_cache

# Create the cache directory so it exists even without a volume mount
RUN mkdir -p /hf_cache

# Non-root user for security
RUN useradd -m appuser && chown -R appuser /app /hf_cache
USER appuser

# -u = unbuffered stdout so print() output appears immediately in docker logs
CMD ["python", "-u", "main.py"]
