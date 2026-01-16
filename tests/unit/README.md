# tests/unit/

Unit tests for **isolated, deterministic functionality** in `src/`.
These tests should cover small, focused pieces of logic without external
dependencies or side effects.

---

## Project-Specific Details (Fill Me In)

### Unit Test Focus Areas

- Core utilities to test:  
- Expected boundary conditions to validate:  
- Critical functions requiring regression tests:  

---

## Purpose

Unit tests ensure that individual components behave correctly under controlled
conditions. They:

- Run very quickly  
- Use only in-memory data  
- Avoid filesystem, network, or external services  
- Detect regressions early in development  

---

## Guidelines

- Keep tests simple and deterministic.  
- Use synthetic, small test data where needed.  
- Avoid mocking unless necessary; prefer pure logic.  
- One logical behavior per test.  
- Filesystem interactions should be mocked or redirected using `tmp_path`.  
