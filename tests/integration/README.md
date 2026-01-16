# tests/integration/

Integration tests for components that interact with **external systems** or
span multiple layers of the ML pipeline (e.g. data → model → evaluation).

These tests validate that the system works as a whole.

---

## Project-Specific Details (Fill Me In)

### Integration Targets

- MLflow tracking / model registry:  
- DVC pipeline steps:  
- Triton or inference endpoints:  
- Data preprocessing + training consistency:  

### Execution Notes

- Which components require mocking vs real services:  
- Temporary resources needed (tmp dirs / docker-compose sandbox):  

---

## Purpose

Integration tests ensure that:

- Pipeline components work together correctly  
- External tools (MLflow, DVC, Triton) interface properly  
- Key workflows behave the same across dev and CI  
- Artifacts produced in one stage are valid for the next  

These tests are slower and more complex than unit tests, but essential for ML projects.

---

## Guidelines

- Use fixtures for MLflow/DVC temporary directories when mocking.  
- Keep external service usage lightweight; avoid full cluster spins.  
- Use minimal synthetic datasets; avoid heavy files.  
- Do not depend on private or production infrastructure during CI.  
