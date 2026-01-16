from __future__ import annotations

from omegaconf import DictConfig

from spatiotemporal_lab.data.datamodule import DataModuleConfig, RandomDataModule
from spatiotemporal_lab.data.datasets import RandomDatasetConfig
from spatiotemporal_lab.data.transforms import Identity


def build_datamodule(cfg: DictConfig) -> RandomDataModule:
    ds_cfg = RandomDatasetConfig(
        n_samples=int(cfg.data.get("n_samples", 1024)),
        n_features=int(cfg.data.get("n_features", 32)),
        n_classes=int(cfg.data.get("n_classes", 2)),
    )
    dm_cfg = DataModuleConfig(
        batch_size=int(cfg.data.get("batch_size", 64)),
        num_workers=int(cfg.data.get("num_workers", 0)),
        pin_memory=bool(cfg.data.get("pin_memory", False)),
        persistent_workers=bool(cfg.data.get("persistent_workers", False)),
        seed=int(cfg.get("seed", 42)),
        val_frac=float(cfg.data.get("val_frac", 0.1)),
        test_frac=float(cfg.data.get("test_frac", 0.1)),
    )
    transform = Identity()
    return RandomDataModule(ds_cfg, dm_cfg, transform=transform)
