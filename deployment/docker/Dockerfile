# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13

# ---- builder ---------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (keep minimal; build-essential only if needed by wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast resolver / installer)
RUN pip install --no-cache-dir uv

# Copy dependency metadata first for better caching
COPY pyproject.toml ./

# Create virtual environment using uv
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Install dependencies (API extra only)
RUN uv pip install --upgrade pip setuptools wheel \
 && uv pip install -e ".[api]"

# Copy source last
COPY src/ ./src/
COPY deployment/api/ ./deployment/api/

# ---- runtime ---------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}" \
    MLFLOW_HOME=/app/.mlflow

WORKDIR /app

# Non-root user for better security
RUN useradd -m -u 10001 appuser \
 && mkdir -p /app/.mlflow \
 && chown -R appuser:appuser /app

# Copy venv + app code
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/deployment/api /app/deployment/api

# Fail-fast entrypoint (no secrets baked into image)
RUN printf '%s\n' \
  '#!/usr/bin/env sh' \
  'set -eu' \
  '' \
  '# Required for registry-backed artifact loading' \
  ': "${MLFLOW_TRACKING_URI:?Missing MLFLOW_TRACKING_URI}"' \
  ': "${MLFLOW_MODEL_NAME:?Missing MLFLOW_MODEL_NAME}"' \
  ': "${MLFLOW_MODEL_ALIAS:=prod}"' \
  '' \
  'exec "$@"' \
  > /usr/local/bin/entrypoint.sh \
 && chmod +x /usr/local/bin/entrypoint.sh

USER appuser

EXPOSE 8000

# Healthcheck endpoint should exist in the API (e.g. GET /health)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()" || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["uvicorn", "deployment.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]