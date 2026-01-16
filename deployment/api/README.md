# API Service (`deployment/api/`)

FastAPI service used for inference.

Features:

- Async-first structure
- `/health` (liveness) and `/ready` (readiness)
- `/metrics` (Prometheus)
- Request ID propagation (`X-Request-ID`)
- Model loading from MLflow Model Registry by alias:
  `models:/${MLFLOW_MODEL_NAME}@${MLFLOW_MODEL_ALIAS}`

Secrets/configuration are injected via environment variables.
For local development, `.env` at repo root may be used.
