"""Streamlit dashboard skeleton.

Best practices:
- Keep UI thin.
- Import reusable logic from `src/` (inference/schemas/integrations).
- Resolve models from MLflow by alias (prod/staging/dev).
"""

from __future__ import annotations

import os

import streamlit as st

# In a real project you would import:
# from spatiotemporal_lab.inference.predictor import Predictor
# from spatiotemporal_lab.integrations.mlflow import ...
# from spatiotemporal_lab.schemas.requests import PredictRequest

st.set_page_config(page_title="Model Dashboard", layout="wide")

st.title("Model Dashboard")
st.caption("Template skeleton: replace with project-specific content.")

with st.sidebar:
    st.header("Model")
    model_name = st.text_input(
        "MLflow model name", os.getenv("MLFLOW_MODEL_NAME", "CHANGE_ME")
    )
    model_alias = st.text_input("Alias", os.getenv("MLFLOW_MODEL_ALIAS", "prod"))

st.write("Model:", model_name, "@", model_alias)

st.subheader("Inputs")
raw = st.text_area("Enter JSON or CSV-like inputs (project-specific)")
st.button("Run inference", disabled=True)

st.info(
    "Implement: load model via MLflow, validate inputs with Pydantic, call predictor, render outputs/plots."
)
