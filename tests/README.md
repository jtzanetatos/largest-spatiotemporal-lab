# tests/

This directory contains the project's **automated test suite**, used to ensure
correctness, reproducibility, stability, and CI validation. All production code
in `src/` should be covered by tests whenever feasible.

---

## Project-Specific Details (Fill Me In)

Complete this section when creating a new project from the template.

### Test Coverage Goals

- Target unit test coverage (%):  
- Core functionality that requires tests:  

### Integration Requirements

- Components requiring integration testing (MLflow, DVC, Triton, APIs):  
- External services needed during integration tests (mocked or real?):  

### Testing Policies

- Mocking strategy (MLflow / DVC / Triton / filesystem):  
- Use of temporary directories or fixtures:  
- Where test datasets live (DVC, small fixtures, synthetic data):  

---

## Purpose

To provide confidence that:

- Core logic in `src/` behaves predictably  
- Changes do not break existing functionality  
- Data processing and training logic is reproducible  
- CI pipelines (Woodpecker) catch errors early  
- Integration with tools like MLflow, DVC, and Triton works as intended  

---

## Recommended Structure

```plain
tests/
  unit/          # Fast, isolated tests of individual functions/classes
  integration/   # Tests involving MLflow, DVC, Triton, or I/O boundaries
  e2e/           # End-to-end tests of full pipelines or workflows (optional)
```

End-to-end (`e2e/`) tests are optional and not included by default, since ML
projects often rely on pipelines rather than monolithic flows.

---

## Best Practices (Shared Across All Repos)

- Unit tests should be **fast**, **pure**, and **stateless**.  
- Integration tests should provide confidence in pipeline-level behavior.  
- Prefer **synthetic test datasets** or fixtures over real domain data.  
- Avoid writing large artifacts during tests; keep test runs lightweight.  
- Use `pytest` fixtures to manage setup/teardown cleanly.  
- Run tests locally before tagging releases.  

---

## Notes

- CI automatically runs `pytest` on each trigger (PR merge, tag, manual run).  
- Avoid storing large test files; use generated or fixture-based data instead.  
