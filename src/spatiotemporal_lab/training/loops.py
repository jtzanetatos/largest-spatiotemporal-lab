from __future__ import annotations

import pytorch_lightning as pl
from loguru import logger
from omegaconf import DictConfig


def build_trainer(cfg: DictConfig) -> pl.Trainer:
    max_epochs = int(cfg.trainer.get("max_epochs", 3))
    accelerator = cfg.trainer.get("accelerator", "auto")
    devices = cfg.trainer.get("devices", "auto")
    log_every_n_steps = int(cfg.trainer.get("log_every_n_steps", 50))
    enable_checkpointing = bool(cfg.trainer.get("enable_checkpointing", True))
    enable_progress_bar = bool(cfg.trainer.get("enable_progress_bar", True))

    return pl.Trainer(
        max_epochs=max_epochs,
        accelerator=accelerator,
        devices=devices,
        log_every_n_steps=log_every_n_steps,
        enable_checkpointing=enable_checkpointing,
        enable_progress_bar=enable_progress_bar,
    )


def fit(
    cfg: DictConfig,
    lightning_module: pl.LightningModule,
    datamodule: pl.LightningDataModule,
) -> pl.Trainer:
    trainer = build_trainer(cfg)
    logger.info("Fitting model...")
    trainer.fit(lightning_module, datamodule=datamodule)
    return trainer
