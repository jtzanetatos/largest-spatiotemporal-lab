# Docker Deployment (`deployment/docker/`)

This directory contains Docker assets for running the project as a **service container** (API serving).
It is intentionally minimal and designed to be “plug-in ready” for a broader platform (K8s stack, ingress, auth, etc.).

Model artifacts are fetched from the **MLflow Model Registry** at runtime (e.g., by alias such as `prod`).

---

## Contents

- `Dockerfile` — builds a runtime image that runs the API server
- `docker-compose.yml` — local development runner (injects configuration via `.env`)
- `.dockerignore` — keeps images small and builds fast

---

## Build context

Both the `Dockerfile` and `docker-compose.yml` are designed to build from the **repo root** as context.

- Compose build context: `../..`
- Manual build (from repo root):

  ```bash
  docker build -f deployment/docker/Dockerfile .
  ```

This allows the image to copy:

- `pyproject.toml`
- `src/`
- `deployment/api/`

---

## Configuration and secrets (opsec)

All runtime configuration should be injected via environment variables.
**Do not commit secrets** (tracking URIs with credentials, tokens, etc.) to the repo.

With docker-compose, use an untracked `.env` file in this directory.

Required environment variables:

- `MLFLOW_TRACKING_URI` — MLflow tracking server URI
- `MLFLOW_MODEL_NAME` — registered model name in the MLflow Model Registry
- `MLFLOW_MODEL_ALIAS` — alias to resolve (recommended: `prod`; default is `prod`)

Example `.env` (DO NOT COMMIT):

```dotenv
MLFLOW_TRACKING_URI=http://127.0.0.1:5000
MLFLOW_MODEL_NAME=my-ml-project
MLFLOW_MODEL_ALIAS=prod
API_PORT=8000
IMAGE_NAME=my-ml-project-api
```

---

## Running locally (docker-compose)

From `deployment/docker/`:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

The API will be available at:

- `http://localhost:${API_PORT:-8000}`

Healthcheck (expected endpoint):

- `GET /health`

---

## Image build (manual)

From the repo root:

```bash
docker build -f deployment/docker/Dockerfile -t my-ml-project-api:latest .
```

Run (example):

```bash
docker run --rm -p 8000:8000 \
  -e MLFLOW_TRACKING_URI="http://127.0.0.1:5000" \
  -e MLFLOW_MODEL_NAME="my-ml-project" \
  -e MLFLOW_MODEL_ALIAS="prod" \
  my-ml-project-api:latest
```

---

## Notes

- The image uses **uv** for faster dependency installation during builds.
- The container includes a **fail-fast entrypoint**: it will exit early if required environment variables are missing.
- The service should load models via:
  - `models:/${MLFLOW_MODEL_NAME}@${MLFLOW_MODEL_ALIAS}`

If you add additional deploy targets (K8s, Helm, Triton), keep this directory focused on Docker packaging only.
