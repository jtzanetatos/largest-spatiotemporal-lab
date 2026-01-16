# NiceGUI Dashboard

This is an optional NiceGUI app used for demos and interactive exploration.

Guidelines:

- UI only; do not implement core logic here.
- Import inference helpers from `src/<spatiotemporal_lab>/inference/`.
- Validate inputs using `src/<spatiotemporal_lab>/schemas/`.
- Keep secrets in `.env` / CI / Kubernetes Secrets.

Run:

```bash
python deployment/dashboards/nicegui/app.py
```
