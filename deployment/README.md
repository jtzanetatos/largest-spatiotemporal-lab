# Deployment

This directory contains **all production deployment assets** for this project.
It is intentionally split by *serving technology* and *deployment target* to keep
concerns clean, composable, and scalable.

The same trained model artifacts (from **MLflow Model Registry**) can be deployed
through different serving paths depending on performance, latency, and operational
requirements.

---

## Directory Structure

```text
deployment/
  docker/        # Containerization for the API service
  api/           # FastAPI inference service (business logic, validation, routing)
  dashboards/    # Optional showcase/operator dashboards (Streamlit / NiceGUI)
  k8s/           # Kubernetes manifests + Helm chart (service-only)
  triton/        # Triton Inference Server model repository + export helpers
```

---

## Deployment Paths

### 1. FastAPI Service (default path)

**Use when:**

- You need flexible inference logic
- You want preprocessing / postprocessing in Python
- Latency is acceptable at the API level
- You expose business endpoints, not just tensor inference

**Stack:**

- FastAPI + Uvicorn
- Docker / Docker Compose
- Kubernetes (Deployment + Service + optional Ingress/HPA)

Artifacts:

- Docker image built from repo root
- Model loaded at runtime from MLflow Registry via aliases (`prod`, `staging`, etc.)

Relevant dirs:

- `deployment/api/`
- `deployment/docker/`
- `deployment/k8s/`

---

### 2. Dashboards (optional)

**Use when:**

- You want a demo UI for stakeholders
- You need a lightweight operator/QA interface
- You want interactive exploration of inputs/outputs/metrics

**Stack options:**

- Streamlit (quick dashboards)
- NiceGUI (app-like dashboards)

Rules:

- Dashboards must remain **thin UIs**
- Reusable logic belongs in `src/`:
  - `src/spatiotemporal_lab/inference/`
  - `src/spatiotemporal_lab/schemas/`
  - `src/spatiotemporal_lab/integrations/`

Relevant dir:

- `deployment/dashboards/`

---

### 3. Triton Inference Server (high-performance path)

**Use when:**

- You need high throughput / low latency tensor inference
- You want GPU batching, dynamic batching, or TensorRT
- You separate inference from business logic

**Stack:**

- NVIDIA Triton Inference Server
- ONNX / TorchScript / TensorRT backends
- Kubernetes or standalone Triton deployment

Artifacts:

- Triton model repository (filesystem layout)
- Models exported from MLflow registry into deployable formats

Relevant dirs:

- `deployment/triton/`

---

## Model Lifecycle (Shared)

All deployment paths rely on **MLflow Model Registry aliases**:

- `dev`       – experimental models
- `staging`   – validated, pre-production
- `prod`      – production-serving
- `archived`  – deprecated models

Promotion rules:

- Models are **exported and validated first**
- Aliases are updated **only after successful export**
- CI enforces one active `prod` alias at a time

---

## Secrets & Configuration

Secrets are **never committed**.

Expected injection methods:

- Local: `.env` file at repo root
- CI: Woodpecker secrets
- Kubernetes: Secrets / ExternalSecrets

Common env vars:

- `MLFLOW_TRACKING_URI`
- `MLFLOW_MODEL_NAME`
- `MLFLOW_MODEL_ALIAS`
- `LOG_LEVEL`, `LOG_FORMAT`

---

## Design Principles

- Build once, deploy everywhere
- Same model → multiple serving backends
- No cluster-specific assumptions
- CI/CD owns promotion, not humans
- Production safety over convenience

This directory is **deployment-ready**, not a full platform stack.
