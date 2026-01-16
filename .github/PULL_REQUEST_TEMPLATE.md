# Summary

What does this PR do and why? (1–3 sentences)

---

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor / internal change
- [ ] Documentation
- [ ] CI / tooling
- [ ] Experiment / research (non-prod)

---

## Related issues / context

Link issues, discussions, or incidents (e.g. #123).

---

## Key changes

- …
- …

---

## Scope and impact

### Affected areas
- [ ] Data / DVC
- [ ] Model / training code
- [ ] Inference / deployment
- [ ] Config (Hydra)
- [ ] Tracking (MLflow)
- [ ] Tests
- [ ] Docs

### Breaking changes
- [ ] None
- [ ] Yes (describe below)

If breaking:
- What changed?
- Migration steps?

---

## Reproducibility & configs

If applicable:
- Hydra command(s) used:
  - `python -m src.<project>.core.train ...`
- Config files added/changed:
  - `config/...`

---

## Data & lineage (if applicable)

- Data source: …
- DVC updated?
  - [ ] No
  - [ ] Yes (what changed: `dvc.yaml` / `dvc.lock` / `.dvc` files)
- Dataset identifiers impacted (`config/data/*.yaml`): …

---

## MLflow (if applicable)

- [ ] No MLflow changes
- [ ] Tracking behavior changed (tags/params/artifacts)
- [ ] Model registry / alias workflow impacted (dev/staging/prod/archived)

Notes:
- Expected experiment name / run naming: …
- New/updated run tags: …

---

## Screenshots / logs / outputs (optional)

Attach any helpful logs, metrics screenshots, or figures.

---

## Testing

What did you run?

- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing
- [ ] Not applicable

Commands / steps:

1. `...`
2. `...`

---

## Checklist

- [ ] Code follows project conventions
- [ ] Tests added/updated where appropriate
- [ ] Docs updated where appropriate
- [ ] Config changes are minimal and composable (Hydra groups/variants)
- [ ] No secrets committed (tokens, credentials, tracking URIs, etc.)
- [ ] CI checks pass