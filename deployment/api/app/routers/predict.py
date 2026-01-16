from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from ..core.logging import request_id_var
from ..schemas.predict import PredictRequest, PredictResponse

router = APIRouter(tags=["inference"])


@router.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest, request: Request) -> PredictResponse:
    svc = request.app.state.model_service
    try:
        outputs = await svc.predict(payload.inputs)
    except Exception as e:
        logger.exception("Prediction failed.")
        raise HTTPException(status_code=500, detail="Prediction failed") from e

    return PredictResponse(
        outputs=outputs, model_uri=svc.model_uri, request_id=request_id_var.get()
    )
