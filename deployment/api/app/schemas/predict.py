from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    inputs: Any = Field(..., description="Model input payload (project-specific).")


class PredictResponse(BaseModel):
    outputs: Any
    model_uri: str
    request_id: Optional[str] = None
