from __future__ import annotations

import pytorch_lightning as pl
from loguru import logger
from omegaconf import DictConfig


def maybe_run_offline_eval(
    cfg: DictConfig,
    trainer: pl.Trainer,
    datamodule: pl.LightningDataModule,
    lightning_module: pl.LightningModule,
) -> None:
    if not bool(cfg.get("evaluation", {}).get("enabled", False)):
        return
    logger.info("Running offline evaluation...")
    trainer.test(lightning_module, datamodule=datamodule)
