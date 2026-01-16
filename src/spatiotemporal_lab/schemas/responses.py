from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class PredictResponse(BaseModel):
    probabilities: List[List[float]] = Field(
        ..., description="Per-class probabilities for each input"
    )
