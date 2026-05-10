"""src/api/app.py — FastAPI application."""

from __future__ import annotations
import logging
import os
import torch
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.utils.config_loader import load_config
from src.utils.logger import setup_logging
from src.api.schemas import (
    AskRequest, AskResponse, HealthResponse, MetricsResponse, ModelVariant
)
from src.api.inference import ModelRegistry, generate

setup_logging()
logger = logging.getLogger("api")

# ── App lifecycle ─────────────────────────────────────────────────────────────

registry: ModelRegistry | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global registry
    cfg      = load_config(os.getenv("CONFIG_PATH", "configs/training_config.yaml"))
    registry = ModelRegistry(cfg)
    logger.info("API started. CUDA=%s", torch.cuda.is_available())
    yield
    logger.info("API shutting down.")


app = FastAPI(
    title="LoRA Fine-Tune Inference API",
    version="1.0.0",
    description="Serve base and LoRA-adapted LLM via a single endpoint.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        cuda=torch.cuda.is_available(),
        base_loaded=registry.base_loaded if registry else False,
        lora_loaded=registry.lora_loaded if registry else False,
    )


@app.post("/ask", response_model=AskResponse, tags=["inference"])
async def ask(req: AskRequest) -> AskResponse:
    if registry is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Registry not ready.")

    try:
        if req.model_variant == ModelVariant.base:
            tokenizer, model = registry.get_base()
            model_id = registry.cfg.model.base_model_id
        else:
            tokenizer, model = registry.get_lora()
            model_id = f"{registry.cfg.model.base_model_id} + LoRA"
    except FileNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        logger.exception("Model load error: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to load model.")

    try:
        answer = generate(
            model, tokenizer,
            instruction=req.instruction,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
            repetition_penalty=req.repetition_penalty,
        )
    except Exception as exc:
        logger.exception("Generation error: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Generation failed.")

    logger.info("variant=%s  tokens=%d  inst=%.60s", req.model_variant, req.max_new_tokens, req.instruction)
    return AskResponse(
        instruction=req.instruction,
        response=answer,
        model_variant=req.model_variant,
        model_id=model_id,
    )


@app.get("/metrics", response_model=MetricsResponse, tags=["evaluation"])
async def metrics() -> MetricsResponse:
    """Return cached evaluation metrics if available."""
    metrics_path = "output/eval_metrics.json"
    if not os.path.exists(metrics_path):
        return MetricsResponse()
    import json
    with open(metrics_path) as fh:
        data = json.load(fh)
    return MetricsResponse(**data)
