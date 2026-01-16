# Dashboards

This directory contains **showcase and operator dashboards** used to:
- demonstrate the solution to stakeholders
- provide lightweight interactive exploration (predictions, metrics, slices)
- support internal QA / demos

Dashboards are **not** the canonical training entrypoint and must not own reusable logic.
They should import:
- inference logic from `src/<spatiotemporal_lab>/inference/`
- schemas from `src/<spatiotemporal_lab>/schemas/`
- tool integrations from `src/<spatiotemporal_lab>/integrations/`

Model artifacts should be resolved from **MLflow Model Registry** (aliases such as `prod`, `staging`).

---

## Structure

```text
deployment/dashboards/
  streamlit/   # Streamlit dashboard app (optional)
  nicegui/     # NiceGUI dashboard app (optional)
```

---

## Secrets and Configuration

Secrets are injected from repo-root `.env` (local) or CI/Kubernetes Secrets:

Common env vars:
- `MLFLOW_TRACKING_URI`
- `MLFLOW_MODEL_NAME`
- `MLFLOW_MODEL_ALIAS` (default: `prod`)
- `LOG_LEVEL`

Never commit credentials or tokens.

---

## Run locally

### Streamlit

```bash
uv pip install -e ".[api]"   # includes mlflow + http client utilities
uv pip install streamlit     # keep dashboards deps optional
streamlit run deployment/dashboards/streamlit/app.py
```

### NiceGUI

```bash
uv pip install -e ".[api]"
uv pip install nicegui
python deployment/dashboards/nicegui/app.py
```

---

## Deployment

Dashboards can be containerized and deployed similarly to the FastAPI service,
but they are considered **optional** and **non-critical path**.
If deployed, treat them as separate services with separate resources and ingress.
