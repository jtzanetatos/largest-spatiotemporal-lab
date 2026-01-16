from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Optional

import mlflow
from loguru import logger
from omegaconf import DictConfig, OmegaConf


def _tracking_uri(cfg: DictConfig) -> Optional[str]:
    # Prefer env var (opsec); fall back to cfg.mlflow.tracking_uri if explicitly set.
    return os.getenv("MLFLOW_TRACKING_URI") or cfg.mlflow.get("tracking_uri")


@contextmanager
def maybe_init_mlflow(cfg: DictConfig):
    if not bool(cfg.mlflow.get("enabled", True)):
        yield None
        return

    uri = _tracking_uri(cfg)
    if uri:
        mlflow.set_tracking_uri(uri)
        logger.info("MLflow tracking URI configured.")
    else:
        logger.warning("MLflow enabled but no tracking URI provided (env or config).")

    exp_name = str(cfg.mlflow.get("experiment_name", cfg.project.name))
    run_name = str(cfg.mlflow.get("run_name", cfg.model.name))

    mlflow.set_experiment(exp_name)
    with mlflow.start_run(run_name=run_name):
        yield


def set_standard_tags(cfg: DictConfig) -> None:
    tags = dict(cfg.mlflow.get("tags", {}))
    tags.setdefault("project", str(cfg.project.name))
    tags.setdefault("env", str(cfg.project.env))
    tags.setdefault("model_name", str(cfg.model.name))
    tags.setdefault("data_name", str(cfg.data.name))
    tags.setdefault("debug", str(bool(cfg.get("debug", False))))
    mlflow.set_tags(tags)


def log_resolved_config(cfg: DictConfig, artifact_path: str = "config") -> None:
    if not bool(cfg.mlflow.get("log_config_as_artifact", True)):
        return
    resolved = OmegaConf.to_yaml(cfg, resolve=True)
    mlflow.log_text(resolved, f"{artifact_path}/resolved.yaml")
