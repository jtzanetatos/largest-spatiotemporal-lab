# INSTRUCTIONS: Architecture Decision Records (ADR)

## Purpose

This directory stores Architecture Decision Records. ADRs capture important technical decisions, the context behind them, and their long-term consequences.

## When to create an ADR

Create an ADR when:

- Choosing tools or frameworks (e.g. Hydra vs plain YAML).
- Selecting infrastructure (e.g. Triton, MLflow, K8s).
- Making architectural trade-offs (performance vs simplicity).
- Changing major design patterns.

## How to use README.md

The `README.md` in this directory is a template:

- It acts as an index of all ADRs.
- It includes a standardized ADR template you should copy for each new decision.

## Best practices

- Use incremental numbering: `adr-0001-...`, `adr-0002-...`
- Keep ADRs short and focused.
- Do not rewrite old ADRs—create a new one and mark previous as superseded.
