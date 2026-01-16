# Triton Model Repository

This directory follows the **NVIDIA Triton Inference Server model repository
specification**.

It is a **build output**, not a source directory.

> Do NOT commit large model artifacts to git.

---

## Structure

```text
model_repository/
  <model_name>/
    config.pbtxt
    <version>/
      model.onnx        # or model.plan / model.pt
```

Example:

```text
model_repository/
  image_classifier/
    config.pbtxt
    17/
      model.onnx
```

---

## Versioning

- Triton versions map **1:1 with MLflow model versions**
- Each version directory is immutable once deployed
- New promotions create new version directories

---

## config.pbtxt

The `config.pbtxt` file defines:

- Model name
- Backend/platform
- Input/output tensors
- Batching configuration
- Instance placement (CPU/GPU)

In this template:

- `config.pbtxt` is **auto‑generated in CI** from the MLflow model signature
- Manual edits should be rare and intentional

---

## CI Integration

The CI pipeline:

1. Resolves a model version from MLflow
2. Exports it to ONNX
3. Writes `config.pbtxt`
4. Validates the repository structure
5. Promotes the MLflow alias (`prod`) only after success

Script:

- `deployment/scripts/promote_and_export_to_triton_updated.py`

---

## Deployment

This directory is mounted into Triton:

```bash
docker run --rm \
  -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -v $(pwd)/deployment/triton/model_repository:/models \
  nvcr.io/nvidia/tritonserver:latest \
  tritonserver --model-repository=/models
```

Kubernetes deployments mount the same directory via PVC or object storage sync.

---

## Notes

- Treat this directory as **artifact output**
- Clean up old versions periodically
- Prefer ONNX for portability
- Use TensorRT only when you control the GPU stack
