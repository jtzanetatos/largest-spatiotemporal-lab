from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from loguru import logger

from .core.logging import configure_logging, request_id_var
from .core.metrics import install_metrics
from .core.model import ModelService, ModelServiceConfig
from .routers import health, predict


def _load_env() -> None:
    """
    Best-practice: secrets and environment-specific settings come from environment variables.
    For local development, optionally load a `.env` file.

    This template prefers a `.env` at the repo root. `find_dotenv(usecwd=True)`
    searches upward from the current working directory.
    """
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_env()
    configure_logging()
    install_metrics(app)

    cfg = ModelServiceConfig.from_env()
    app.state.model_service = ModelService(cfg)

    if cfg.load_on_startup:
        try:
            await app.state.model_service.load()
            logger.info("Model loaded and ready.")
        except Exception:
            # Keep process alive but mark readiness as false.
            logger.exception(
                "Failed to load model on startup; readiness will be false."
            )

    yield

    try:
        await app.state.model_service.close()
    except Exception:
        logger.exception("Error during shutdown.")


app = FastAPI(
    title=os.getenv("APP_NAME", "ml-template-api"),
    version=os.getenv("APP_VERSION", "0.1.0"),
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    rid = request.headers.get("x-request-id") or request.headers.get("x-requestid")
    if not rid:
        import uuid

        rid = str(uuid.uuid4())

    token = request_id_var.set(rid)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
    finally:
        request_id_var.reset(token)


app.include_router(health.router)
app.include_router(predict.router)


@app.get("/", tags=["meta"])
async def root() -> dict[str, Any]:
    return {
        "name": app.title,
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics",
    }
