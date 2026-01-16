# MLflow Configuration (`config/mlflow/`)

This directory defines **MLflow Tracking configuration** used by the project.
MLflow is the canonical experiment tracker in this template (parameters, metrics, artifacts, and run metadata).

This template follows **Pattern A (recommended)**:

- MLflow configuration lives in this group.
- The training entrypoint is responsible for:
  - resolving the tracking URI from the environment
  - selecting or creating an experiment
  - starting and ending runs
  - applying tags
  - logging params, metrics, artifacts, models, and datasets

Hydra run directories are configured in `config/config.yaml` and are orthogonal to MLflow tracking.

---

## What MLflow supports (high-level)

MLflow Tracking can log:

- **Parameters** and **metrics** for runs
- **Tags** for organization and search
- **Artifacts** (files, plots, checkpoints, serialized objects)
- **Datasets** as first-class tracked inputs (name, digest, schema, source)
- Remote tracking via `MLFLOW_TRACKING_URI` or `mlflow.set_tracking_uri()`

Server-side concerns (backend store, artifact store, default artifact root) are configured when running
`mlflow server` and are not stored in this repository.

---

## Tracking URI and security (important)

- The MLflow tracking URI is resolved from the environment variable `MLFLOW_TRACKING_URI`.
- No tracking endpoints, credentials, or secrets are stored in version-controlled config.
- Use `.env` files, shell exports, Docker secrets, or CI/CD secret stores to configure MLflow.
- CLI overrides of the tracking URI are supported for **local debugging only** and are discouraged for production use.

---

## Model lifecycle and registry (aliases)

This template manages model lifecycle using **MLflow Model Registry aliases** (preferred over deprecated model stages).

Supported lifecycle aliases:

- **`dev`** — experimental or candidate models (performance not yet validated)
- **`staging`** — validated models under refinement or hyperparameter tuning
- **`prod`** — approved models for production deployment
- **`archived`** — retired models (must not be deployed)

Lifecycle state is attached to **model versions**, not runs.
Promotion between lifecycle states is handled outside training (e.g. CI pipelines or manual approval).

Deployments should always resolve models via aliases, for example:

```text
models:/<model_name>@prod
```

---

## Conventions used in this template

- **Experiment name**: project-level and stable (default: `${project.name}`)
- **Run name**: model-level (default: `${model.name}`)
- **Run tags**: standardized minimal set
  - `project`
  - `env`
  - `model_name`
  - `data_name`
  - `debug`
  - `lifecycle_intent` (training-time intent only)

- **Dataset lineage**:
  - Config provides stable dataset identifiers (from `config/data/...`)
  - Runtime code logs dynamic lineage (Git SHA, DVC metadata, dataset digest)

---

## Usage examples

```bash
# Default tracking configuration
python -m src.spatiotemporal_lab.core.train

# Disable MLflow (useful for quick local debugging)
python -m src.spatiotemporal_lab.core.train mlflow.enabled=false

# LOCAL DEBUG ONLY: override tracking server
python -m src.spatiotemporal_lab.core.train mlflow.tracking_uri=http://127.0.0.1:5000
```

---

## Notes

- For remote tracking servers, always prefer configuring `MLFLOW_TRACKING_URI` via the environment.
- Dataset tracking uses MLflow dataset primitives (`mlflow.data`) that include a digest/fingerprint.
- Model promotion and deployment should rely on registry aliases, not run metadata.
