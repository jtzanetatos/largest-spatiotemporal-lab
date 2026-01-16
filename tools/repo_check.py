#!/usr/bin/env python3
"""
Repository structure validator (template-friendly).

Purpose
- Provide a fast, deterministic check that the repo matches the template expectations.
- Intended for local use and CI.

What it checks (high level)
- Required top-level files/dirs exist
- Expected config groups exist (Hydra)
- Deployment skeleton present (docker/api/k8s/triton)
- Testing skeleton present
- GitHub community health files present (optional but recommended)

Exit codes
- 0: OK
- 1: Missing required items
- 2: Found issues (non-fatal warnings treated as errors if --strict)
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Tuple

REPO_ROOT = Path.cwd()


def exists(path: Path) -> bool:
    return path.exists()


def check_required_paths(required: Iterable[Path]) -> List[str]:
    missing = []
    for p in required:
        if not exists(p):
            missing.append(str(p))
    return missing


def check_any_exists(group_name: str, candidates: Iterable[Path]) -> Tuple[bool, str]:
    for p in candidates:
        if exists(p):
            return True, str(p)
    return (
        False,
        f"{group_name}: none of {', '.join(str(c) for c in candidates)} exists",
    )


def warn(msg: str, warnings: List[str]) -> None:
    warnings.append(msg)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate repository structure against the ML template."
    )
    ap.add_argument("--root", default=str(REPO_ROOT), help="Repo root (default: cwd)")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: root does not exist: {root}")
        return 1

    missing_required: List[str] = []
    warnings: List[str] = []

    # --- top-level ---
    required_top = [
        root / "pyproject.toml",
        root / "README.md",
        root / "src",
        root / "tests",
        root / "config",
        root / "deployment",
        root / "notebooks",
    ]
    missing_required += check_required_paths(required_top)

    # --- Hydra config entrypoint ---
    required_config = [
        root / "config" / "config.yaml",
        root / "config" / "README.md",
        root / "config" / "data" / "base.yaml",
        root / "config" / "data" / "README.md",
        root / "config" / "model" / "README.md",
        root / "config" / "trainer" / "README.md",
        root / "config" / "logging" / "README.md",
        root / "config" / "mlflow" / "README.md",
        root / "config" / "experiment" / "README.md",
    ]
    missing_required += check_required_paths(required_config)

    # --- deployment skeleton ---
    required_deploy = [
        root / "deployment" / "README.md",
        root / "deployment" / "api" / "README.md",
        root / "deployment" / "docker" / "README.md",
        root / "deployment" / "k8s" / "README.md",
        root / "deployment" / "triton" / "README.md",
        root / "deployment" / "triton" / "model_repository" / "README.md",
    ]
    missing_required += check_required_paths(required_deploy)

    # Optional but recommended deployment files
    optional_deploy_groups = [
        (
            "Dockerfile",
            [
                root / "deployment" / "docker" / "Dockerfile",
                root / "deployment" / "Dockerfile",
            ],
        ),
        (
            "docker-compose",
            [
                root / "deployment" / "docker" / "docker-compose.yml",
                root / "docker-compose.yml",
            ],
        ),
    ]
    for name, candidates in optional_deploy_groups:
        ok, msg = check_any_exists(name, candidates)
        if not ok:
            warn(f"WARN: {msg}", warnings)

    # --- tests structure ---
    required_tests = [
        root / "tests" / "README.md",
        root / "tests" / "unit" / "README.md",
        root / "tests" / "integration" / "README.md",
    ]
    missing_required += check_required_paths(required_tests)

    # --- notebooks readme ---
    missing_required += check_required_paths([root / "notebooks" / "README.md"])

    # --- docs/data top-level readmes (recommended) ---
    if not (root / "docs" / "README.md").exists():
        warn("WARN: docs/README.md missing (recommended).", warnings)
    if not (root / "data" / "README.md").exists():
        warn("WARN: data/README.md missing (recommended).", warnings)

    # --- community health files (recommended) ---
    gh = root / ".github"
    if gh.exists():
        if not (gh / "PULL_REQUEST_TEMPLATE.md").exists():
            warn(
                "WARN: .github/PULL_REQUEST_TEMPLATE.md missing (recommended).",
                warnings,
            )
        issue_dir = gh / "ISSUE_TEMPLATE"
        if not issue_dir.exists():
            warn("WARN: .github/ISSUE_TEMPLATE/ missing (recommended).", warnings)
        else:
            # config.yml is optional; templates are recommended
            for f in ["bug_report.yml", "feature_request.yml", "task.yml"]:
                if not (issue_dir / f).exists():
                    warn(
                        f"WARN: .github/ISSUE_TEMPLATE/{f} missing (recommended).",
                        warnings,
                    )
    else:
        warn("WARN: .github/ directory missing (recommended).", warnings)

    # --- woodpecker (optional but expected if using it) ---
    if (
        not (root / ".woodpecker.yml").exists()
        and not (root / ".woodpecker" / "cli.yml").exists()
    ):
        warn(
            "WARN: no Woodpecker pipeline found (.woodpecker.yml or .woodpecker/cli.yml).",
            warnings,
        )

    # --- report ---
    if missing_required:
        print("ERROR: missing required paths:")
        for p in missing_required:
            print(f"  - {p}")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")

    if missing_required:
        return 1
    if warnings and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
