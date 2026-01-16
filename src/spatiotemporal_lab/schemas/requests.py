from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    inputs: List[List[float]] = Field(..., description="Batch of feature vectors")
