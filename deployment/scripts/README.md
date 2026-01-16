# scripts/

This directory contains automation and utility scripts used for **model
promotion, export, validation, and deployment**.

Scripts here orchestrate the full workflow from MLflow → Triton → runtime
environments.

## Project-Specific Details (Fill Me In)

**Promotion Workflow**

- Registered MLflow model name(s):  
- Export format(s) required (ONNX / TorchScript / SavedModel):  
- Additional preprocessing for export (if any):  

**Environment Requirements**

- Python version:  
- External tools needed (ONNX Runtime, Torch, TensorFlow):  

## Purpose

Provide reliable command-line tools for:

- Promoting MLflow model versions  
- Exporting models into Triton-ready formats  
- Generating Triton config files (`config.pbtxt`)  
- Validating exported models  
- Running simple deployment checks  

These scripts enable automation via CI/CD pipelines and local development.

## Best Practices

- Keep scripts **idempotent**: running twice should not corrupt the repo.  
- Avoid hardcoding paths; use config files or environment variables.  
- Log steps clearly for CI use.  
- Ensure scripts fail fast with clear error messages.  

## Notes

Scripts are intended to run from the repository root:

```bash
python -m deployment.scripts.promote_and_export --version 3
```
