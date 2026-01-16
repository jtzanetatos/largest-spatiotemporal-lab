from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request):
    svc = request.app.state.model_service
    return {"ready": bool(svc.ready), "model_uri": svc.model_uri}
