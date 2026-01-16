# Kubernetes Deployment (`deployment/k8s/`)

This directory contains Kubernetes deployment assets for the API service.

Design goals:
- **Namespace-agnostic** (no hardcoded namespaces)
- **Service-only** (ready to plug into a broader cluster stack)
- Supports both:
  - **Kustomize** manifests (`base/`, optional `overlays/`)
  - **Helm** chart (`helm/`) — recommended for deployments
- **No secrets in git**: MLflow settings come from env vars via ConfigMap + existing Secret / ExternalSecrets.

Service contract (container env vars):
- `MLFLOW_TRACKING_URI` (secret)
- `MLFLOW_MODEL_NAME` (config)
- `MLFLOW_MODEL_ALIAS` (config; default `prod`)
- optional: `LOG_LEVEL`, `LOG_FORMAT`, `APP_ENV`, `LOAD_MODEL_ON_STARTUP`

Health endpoints:
- Liveness: `GET /health`
- Readiness: `GET /ready`
- Metrics: `GET /metrics`

---

## Kustomize (base)

From repo root:

```bash
kubectl apply -k deployment/k8s/base
```

Enable optional resources (HPA/Ingress) by adding them in overlays or using Helm.

---

## Helm (recommended)

From repo root:

```bash
helm install my-ml-service deployment/k8s/helm -n <namespace> --create-namespace
```

Enable ingress / hpa (both disabled by default):

```bash
helm upgrade --install my-ml-service deployment/k8s/helm -n <namespace> \
  --set ingress.enabled=true \
  --set hpa.enabled=true
```

Use an existing Secret (recommended), e.g. created by ExternalSecrets:

```bash
helm upgrade --install my-ml-service deployment/k8s/helm -n <namespace> \
  --set secrets.existingSecret=mlflow-secrets
```
