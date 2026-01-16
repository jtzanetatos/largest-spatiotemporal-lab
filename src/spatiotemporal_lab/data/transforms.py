from __future__ import annotations

import torch


class Identity:
    def __call__(self, x):
        return x


def to_float32(x: torch.Tensor) -> torch.Tensor:
    return x.to(torch.float32)


def compose(*fns):
    def _c(x):
        for fn in fns:
            x = fn(x)
        return x

    return _c
