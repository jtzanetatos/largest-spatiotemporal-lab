"""NiceGUI dashboard skeleton.

Best practices:
- Keep UI thin.
- Import reusable logic from `src/` (inference/schemas/integrations).
- Resolve models from MLflow by alias (prod/staging/dev).
"""

from __future__ import annotations

import os

from nicegui import ui

# In a real project you would import:
# from spatiotemporal_lab.inference.predictor import Predictor
# from spatiotemporal_lab.schemas.requests import PredictRequest

ui.page_title("Model Dashboard")

with ui.column().classes("w-full items-start"):
    ui.label("Model Dashboard").classes("text-2xl font-bold")
    ui.label("Template skeleton: replace with project-specific content.").classes(
        "text-sm text-gray-500"
    )

    model_name = ui.input(
        "MLflow model name", value=os.getenv("MLFLOW_MODEL_NAME", "CHANGE_ME")
    )
    model_alias = ui.input("Alias", value=os.getenv("MLFLOW_MODEL_ALIAS", "prod"))

    ui.separator()

    ui.label("Inputs")
    inp = ui.textarea(
        placeholder="Enter JSON or CSV-like inputs (project-specific)"
    ).classes("w-full")

    def _run():
        ui.notify("Inference not implemented in template.", type="warning")

    ui.button("Run inference", on_click=_run)

ui.run(host="0.0.0.0", port=8080)
