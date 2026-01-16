from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import pytorch_lightning as pl
from torch.utils.data import DataLoader, Subset

from spatiotemporal_lab.data.datasets import RandomClassificationDataset, RandomDatasetConfig
from spatiotemporal_lab.data.splits import random_split_indices
from spatiotemporal_lab.data.transforms import Identity


@dataclass(frozen=True)
class DataModuleConfig:
    batch_size: int = 64
    num_workers: int = 0
    pin_memory: bool = False
    persistent_workers: bool = False
    seed: int = 42
    val_frac: float = 0.1
    test_frac: float = 0.1


class RandomDataModule(pl.LightningDataModule):
    def __init__(
        self,
        ds_cfg: RandomDatasetConfig,
        dm_cfg: DataModuleConfig,
        transform: Optional[Callable] = None,
    ):
        super().__init__()
        self.ds_cfg = ds_cfg
        self.dm_cfg = dm_cfg
        self.transform = transform or Identity()
        self._dataset = None
        self._split = None

    def setup(self, stage: Optional[str] = None) -> None:
        self._dataset = RandomClassificationDataset(
            self.ds_cfg, transform=self.transform, seed=self.dm_cfg.seed
        )
        self._split = random_split_indices(
            n=len(self._dataset),
            seed=self.dm_cfg.seed,
            val_frac=self.dm_cfg.val_frac,
            test_frac=self.dm_cfg.test_frac,
        )

    def train_dataloader(self):
        assert self._dataset is not None and self._split is not None
        return DataLoader(
            Subset(self._dataset, self._split.train_idx),
            batch_size=self.dm_cfg.batch_size,
            shuffle=True,
            num_workers=self.dm_cfg.num_workers,
            pin_memory=self.dm_cfg.pin_memory,
            persistent_workers=self.dm_cfg.persistent_workers,
        )

    def val_dataloader(self):
        assert self._dataset is not None and self._split is not None
        return DataLoader(
            Subset(self._dataset, self._split.val_idx),
            batch_size=self.dm_cfg.batch_size,
            shuffle=False,
            num_workers=self.dm_cfg.num_workers,
            pin_memory=self.dm_cfg.pin_memory,
            persistent_workers=self.dm_cfg.persistent_workers,
        )

    def test_dataloader(self):
        assert self._dataset is not None and self._split is not None
        return DataLoader(
            Subset(self._dataset, self._split.test_idx),
            batch_size=self.dm_cfg.batch_size,
            shuffle=False,
            num_workers=self.dm_cfg.num_workers,
            pin_memory=self.dm_cfg.pin_memory,
            persistent_workers=self.dm_cfg.persistent_workers,
        )
