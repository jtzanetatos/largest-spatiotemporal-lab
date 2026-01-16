from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass
class Predictor:
    model: nn.Module
    device: str = "cpu"

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        self.model.eval()
        with torch.no_grad():
            x = x.to(self.device)
            logits = self.model(x)
            return logits.softmax(dim=-1)
