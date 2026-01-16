#!/usr/bin/env python3
"""
Data layout + hygiene validator (template-friendly, stdlib only).

Purpose
- Validate that the repo's `data/` directory and related metadata follow the
  template's best-practice conventions.
- Safe for CI: does NOT download data, does NOT run pipelines, does NOT mutate files.

Checks
1) Directory structure:
   - data/ exists
   - data/README.md exists (required)
   - raw/ processed/ external/ are optional

2) DVC hygiene (only if DVC appears to be used):
   - if `dvc.yaml` or `.dvc/` exists:
       - `.dvc/` exists
       - `.gitignore` contains a rule ignoring `data/` (or its contents)
   - no calls to `dvc` CLI; structure-only

3) Large file guard:
   - scans `data/` and fails if files > threshold are found
   - exception: `.dvc` pointer files (small, text)
   - supports --warn-only for template repos early on

4) Config cross-check (optional):
   - if --check-config:
       - attempts to parse `config/data/base.yaml` (very small YAML subset)
       - validates referenced paths exist
   - stdlib-only parsing; expects simple `key: value` structure for paths

Exit codes
- 0: OK
- 1: Errors (missing required items / large files / config path missing)
- 2: Warnings treated as errors (--strict)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


def human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    f = float(n)
    for u in units:
        if f < 1024.0 or u == units[-1]:
            return f"{f:.1f}{u}" if u != "B" else f"{int(f)}B"
        f /= 1024.0
    return f"{n}B"


def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    while p != p.parent:
        if (p / "pyproject.toml").exists() or (p / ".git").exists():
            return p
        p = p.parent
    return start.resolve()


def appears_to_use_dvc(root: Path) -> bool:
    return (root / "dvc.yaml").exists() or (root / ".dvc").exists()


def gitignore_ignores_data(gitignore: Path) -> bool:
    if not gitignore.exists():
        return False
    txt = gitignore.read_text(encoding="utf-8", errors="ignore")
    # very small heuristic: look for lines that ignore data/ or /data/
    patterns = [
        r"^data/$",
        r"^/data/$",
        r"^data/\*$",
        r"^/data/\*$",
        r"^data/\*\*$",
        r"^/data/\*\*$",
        r"^data/\*\*/\*$",
        r"^/data/\*\*/\*$",
        r"^data/\*\*/\*\*$",
    ]
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for pat in patterns:
            if re.fullmatch(pat, line):
                return True
    # Also accept a looser match that ignores the data directory generally.
    if re.search(r"(^|\n)\s*/?data/\s*(\n|$)", txt):
        return True
    return False


def scan_large_files(data_dir: Path, threshold_bytes: int) -> List[Tuple[Path, int]]:
    large: List[Tuple[Path, int]] = []
    if not data_dir.exists():
        return large
    for p in data_dir.rglob("*"):
        if not p.is_file():
            continue
        # ignore git internals
        if ".git" in p.parts:
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        # Allow .dvc pointer files (they should be small anyway, but we never fail on them)
        if p.suffix == ".dvc":
            continue
        if size > threshold_bytes:
            large.append((p, size))
    return large


def parse_simple_yaml_kv(path: Path) -> Dict[str, str]:
    """
    Minimal YAML key: value parser (stdlib-only).
    Assumptions:
    - no lists
    - no multiline values
    - indentation denotes nesting, which we flatten with dot keys (e.g. paths.data_dir)
    - comments (# ...) are ignored
    This is intentionally conservative and only used for optional path checks.
    """
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    stack: List[Tuple[int, str]] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        m = re.match(r"^(\s*)([^:]+):(.*)$", line)
        if not m:
            continue
        indent = len(m.group(1))
        key = m.group(2).strip()
        val = m.group(3).strip()
        # unwind stack
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if val == "":
            # parent key
            stack.append((indent, key))
            continue
        # strip quotes
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        full_key = ".".join([k for _, k in stack] + [key])
        out[full_key] = val
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate data/ directory structure and hygiene."
    )
    ap.add_argument(
        "--root", default=None, help="Repo root (default: auto-detect from cwd)"
    )
    ap.add_argument(
        "--threshold-mb",
        type=int,
        default=50,
        help="Large file threshold in MB (default: 50)",
    )
    ap.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    ap.add_argument(
        "--warn-only",
        action="store_true",
        help="Do not fail on large files; warn instead.",
    )
    ap.add_argument(
        "--check-config",
        action="store_true",
        help="Cross-check config/data/base.yaml paths exist.",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else find_repo_root(Path.cwd())
    data_dir = root / "data"
    cfg_path = root / "config" / "data" / "base.yaml"

    errors: List[str] = []
    warnings: List[str] = []

    # 1) Directory structure
    if not data_dir.exists():
        errors.append(f"Missing data/ directory: {data_dir}")
    else:
        if not (data_dir / "README.md").exists():
            errors.append("Missing required data/README.md")
        # Optional dirs are fine; we don't enforce.

    # 2) DVC hygiene
    if appears_to_use_dvc(root):
        if not (root / ".dvc").exists():
            errors.append(
                "DVC appears to be used (dvc.yaml or .dvc present) but .dvc/ directory is missing."
            )
        gi = root / ".gitignore"
        if not gitignore_ignores_data(gi):
            warnings.append(
                ".gitignore does not appear to ignore data/ (recommended when using DVC)."
            )

    # 3) Large file guard
    threshold_bytes = int(args.threshold_mb) * 1024 * 1024
    large = scan_large_files(data_dir, threshold_bytes)
    if large:
        msg_lines = [f"Found large files in data/ (> {args.threshold_mb}MB):"]
        for p, sz in sorted(large, key=lambda t: t[1], reverse=True):
            rel = p.relative_to(root)
            msg_lines.append(f"  - {rel} ({human_bytes(sz)})")
        msg = "\n".join(msg_lines)
        if args.warn_only:
            warnings.append(msg)
        else:
            errors.append(msg)

    # 4) Config cross-check
    if args.check_config:
        if not cfg_path.exists():
            warnings.append(f"Config cross-check enabled but missing: {cfg_path}")
        else:
            kv = parse_simple_yaml_kv(cfg_path)

            # Heuristic: check common keys used in template configs
            candidate_keys = [
                "paths.data_dir",
                "paths.raw_dir",
                "paths.processed_dir",
                "paths.external_dir",
                "data.paths.data_dir",
                "data.paths.raw_dir",
                "data.paths.processed_dir",
                "data.paths.external_dir",
                "data.path",
                "data.data_dir",
            ]
            checked_any = False
            for k in candidate_keys:
                if k in kv:
                    checked_any = True
                    raw_val = kv[k]
                    # Support relative paths
                    p = Path(raw_val)
                    resolved = (root / p) if not p.is_absolute() else p
                    if not resolved.exists():
                        errors.append(
                            f"Config path missing: {k}={raw_val} (resolved: {resolved})"
                        )
            if not checked_any:
                warnings.append(
                    "Config cross-check enabled but no known data path keys were found in config/data/base.yaml. "
                    "(This is OK if your schema differs.)"
                )

    # Report
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"- {e}")
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"- {w}")

    if errors:
        return 1
    if warnings and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
