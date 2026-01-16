from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import anyio
import mlflow
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


@dataclass(frozen=True)
class ModelServiceConfig:
    tracking_uri: str
    model_name: str
    model_alias: str = "prod"
    load_on_startup: bool = True

    @staticmethod
    def from_env() -> "ModelServiceConfig":
        tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
        model_name = os.environ["MLFLOW_MODEL_NAME"]
        model_alias = os.getenv("MLFLOW_MODEL_ALIAS", "prod")
        load_on_startup = os.getenv("LOAD_MODEL_ON_STARTUP", "true").lower() in (
            "1",
            "true",
            "yes",
        )
        return ModelServiceConfig(
            tracking_uri=tracking_uri,
            model_name=model_name,
            model_alias=model_alias,
            load_on_startup=load_on_startup,
        )


class ModelService:
    """Loads and serves a model artifact from MLflow Model Registry by alias."""

    def __init__(self, cfg: ModelServiceConfig):
        self.cfg = cfg
        self._model: Optional[Any] = None

    @property
    def ready(self) -> bool:
        return self._model is not None

    @property
    def model_uri(self) -> str:
        return f"models:/{self.cfg.model_name}@{self.cfg.model_alias}"

    def _configure_mlflow(self) -> None:
        mlflow.set_tracking_uri(self.cfg.tracking_uri)

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=10),
        retry=retry_if_exception_type(Exception),
    )
    def _load_sync(self) -> Any:
        self._configure_mlflow()
        uri = self.model_uri
        logger.info("Loading model from MLflow registry: {}", uri)
        return mlflow.pyfunc.load_model(uri)

    async def load(self) -> None:
        if self._model is not None:
            return
        self._model = await anyio.to_thread.run_sync(self._load_sync)

    async def close(self) -> None:
        return

    async def predict(self, inputs: Any) -> Any:
        if self._model is None:
            await self.load()

        def _predict_sync():
            return self._model.predict(inputs)

        return await anyio.to_thread.run_sync(_predict_sync)
