from __future__ import annotations

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


def install_metrics(app: FastAPI) -> None:
    """Adds /metrics endpoint and minimal request metrics middleware."""

    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        method = request.method
        path = request.url.path
        with REQUEST_LATENCY.labels(method=method, path=path).time():
            response = await call_next(request)
        REQUEST_COUNT.labels(
            method=method, path=path, status=str(response.status_code)
        ).inc()
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
