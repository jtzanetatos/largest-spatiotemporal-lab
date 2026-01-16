"""Hydra training entrypoint.

This is the canonical, reproducible training runner.
Notebooks should call into this (or import its components), not re-implement it.
"""

from __future__ import annotations

from pathlib import Path

import hydra
from hydra.core.hydra_config import HydraConfig
from loguru import logger
from omegaconf import DictConfig

from spatiotemporal_lab.data.factory import build_datamodule
from spatiotemporal_lab.evaluation.evaluate import maybe_run_offline_eval
from spatiotemporal_lab.integrations.mlflow import (
    log_resolved_config,
    maybe_init_mlflow,
    set_standard_tags,
)
from spatiotemporal_lab.models.factory import build_lightning_module
from spatiotemporal_lab.training.loops import fit
from spatiotemporal_lab.utils.seed import seed_everything


@hydra.main(
    version_base=None,
    config_path=str(Path(__file__).resolve().parents[3] / "config"),
    config_name="config",
)
def main(cfg: DictConfig) -> None:
    logger.info("Project: {} (env={})", cfg.project.name, cfg.project.env)
    logger.info("Model:   {}", cfg.model.name)
    logger.info("Data:    {}", cfg.data.name)
    logger.info("Debug:   {}", cfg.get("debug", False))

    seed_everything(int(cfg.get("seed", 42)))

    run_dir = Path(HydraConfig.get().runtime.output_dir)
    logger.info("Run dir: {}", run_dir)

    mlflow_ctx = maybe_init_mlflow(cfg)
    if mlflow_ctx is not None:
        with mlflow_ctx:
            set_standard_tags(cfg)
            log_resolved_config(cfg, artifact_path="config")
            _run_training(cfg)
    else:
        _run_training(cfg)


def _run_training(cfg: DictConfig) -> None:
    dm = build_datamodule(cfg)
    lm = build_lightning_module(cfg)

    trainer = fit(cfg, lightning_module=lm, datamodule=dm)

    maybe_run_offline_eval(cfg, trainer=trainer, datamodule=dm, lightning_module=lm)


if __name__ == "__main__":
    main()
