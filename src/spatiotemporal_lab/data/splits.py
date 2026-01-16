from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Split:
    train_idx: np.ndarray
    val_idx: np.ndarray
    test_idx: np.ndarray


def random_split_indices(
    n: int, seed: int = 42, val_frac: float = 0.1, test_frac: float = 0.1
) -> Split:
    assert (
        0.0 <= val_frac < 1.0 and 0.0 <= test_frac < 1.0 and val_frac + test_frac < 1.0
    )
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    n_test = int(n * test_frac)
    n_val = int(n * val_frac)
    test = idx[:n_test]
    val = idx[n_test : n_test + n_val]
    train = idx[n_test + n_val :]
    return Split(train, val, test)
