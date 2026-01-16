from __future__ import annotations

import torch


def accuracy(logits: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    return (logits.argmax(dim=1) == y).float().mean()
