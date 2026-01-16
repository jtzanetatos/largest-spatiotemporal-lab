# Streamlit Dashboard

This is an optional Streamlit app used for demos and lightweight exploration.

Guidelines:

- UI only; do not implement core logic here.
- Import inference helpers from `src/<spatiotemporal_lab>/inference/`.
- Validate user inputs using `src/<spatiotemporal_lab>/schemas/`.
- Resolve models from MLflow via aliases (`prod`, `staging`, etc.).

Run:

```bash
streamlit run deployment/dashboards/streamlit/app.py
```
