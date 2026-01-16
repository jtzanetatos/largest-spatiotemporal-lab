#!/usr/bin/env python3
"""
Release helper for template repos.

This script performs a safe, reproducible release by:
- Ensuring git working tree is clean
- Ensuring you are on the expected branch (default: main)
- Optionally running quality gates (ruff + pytest) before tagging
- Bumping version in pyproject.toml ([project].version is the source of truth)
- Committing the version bump
- Creating an annotated tag (default: vX.Y.Z)
- Pushing commit + tag

Notes
- This repo uses PEP 621: version lives in pyproject.toml under [project].version
- No requirements.txt is used; this script assumes your local env already has:
  - tomlkit (dev dependency)
  - ruff / pytest (optional checks)
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tomlkit import dumps, parse  # dev dependency

PYPROJECT = Path("pyproject.toml")


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    @staticmethod
    def parse(s: str) -> "Version":
        m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", s.strip())
        if not m:
            raise ValueError(f"Invalid version '{s}'. Expected format: X.Y.Z")
        return Version(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    def bump(self, part: str) -> "Version":
        if part == "major":
            return Version(self.major + 1, 0, 0)
        if part == "minor":
            return Version(self.major, self.minor + 1, 0)
        if part == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        raise ValueError("part must be one of: major, minor, patch")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def run(
    cmd: list[str], *, capture: bool = False, check: bool = True
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        text=True,
        capture_output=capture,
        check=check,
    )


def git(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return run(["git", *args], capture=capture)


def ensure_git_repo() -> None:
    try:
        git("rev-parse", "--is-inside-work-tree")
    except subprocess.CalledProcessError as e:
        raise SystemExit("Not a git repository (or git not available).") from e


def current_branch() -> str:
    res = git("rev-parse", "--abbrev-ref", "HEAD", capture=True)
    return res.stdout.strip()


def ensure_branch(expected: str) -> None:
    br = current_branch()
    if br != expected:
        raise SystemExit(
            f"Refusing to release from branch '{br}'. Expected '{expected}'."
        )


def ensure_clean_working_tree() -> None:
    # porcelain is stable for parsing
    res = git("status", "--porcelain", capture=True)
    if res.stdout.strip():
        raise SystemExit(
            "Working tree is not clean. Commit/stash changes before releasing."
        )


def read_version_from_pyproject(path: Path = PYPROJECT) -> Version:
    if not path.exists():
        raise SystemExit(f"Missing {path}.")
    doc = parse(path.read_text(encoding="utf-8"))
    try:
        v = doc["project"]["version"]
    except Exception as e:
        raise SystemExit(
            "pyproject.toml missing [project].version (source of truth)."
        ) from e
    return Version.parse(str(v))


def write_version_to_pyproject(new_version: Version, path: Path = PYPROJECT) -> None:
    doc = parse(path.read_text(encoding="utf-8"))
    doc["project"]["version"] = str(new_version)
    path.write_text(dumps(doc), encoding="utf-8")


def tag_name(version: Version, prefix: str) -> str:
    return f"{prefix}{version}"


def check_tag_does_not_exist(tag: str) -> None:
    res = git("tag", "--list", tag, capture=True)
    if res.stdout.strip():
        raise SystemExit(f"Tag already exists: {tag}")


def run_checks(*, skip: bool) -> None:
    if skip:
        return

    # Prefer running whatever is available in the active environment.
    # This template expects ruff + pytest as dev deps.
    print("Running ruff + pytest...")
    try:
        run(["ruff", "check", "."])
        run(["ruff", "format", "--check", "."])
    except FileNotFoundError:
        raise SystemExit(
            "ruff is not available in this environment. Install dev deps or use --skip-checks."
        )

    # pytest: treat "no tests collected" (exit 5) as success for templates
    try:
        p = subprocess.run(["pytest"], text=True)
        if p.returncode == 5:
            print("pytest: no tests collected (exit code 5). Treating as success.")
        elif p.returncode != 0:
            raise SystemExit(f"pytest failed with exit code {p.returncode}")
    except FileNotFoundError:
        raise SystemExit(
            "pytest is not available in this environment. Install dev deps or use --skip-checks."
        )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Safe release helper (bump version, tag, push)."
    )
    ap.add_argument(
        "--part",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Which part to bump.",
    )
    ap.add_argument(
        "--set-version",
        default=None,
        help="Set an explicit version X.Y.Z instead of bumping.",
    )
    ap.add_argument(
        "--branch", default="main", help="Branch required for release (default: main)."
    )
    ap.add_argument(
        "--tag-prefix", default="v", help="Tag prefix (default: v -> vX.Y.Z)."
    )
    ap.add_argument(
        "--skip-checks", action="store_true", help="Skip ruff/pytest checks."
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="Print actions without making changes."
    )
    ap.add_argument(
        "--no-push", action="store_true", help="Do not push commit/tag (local-only)."
    )
    ap.add_argument(
        "--message", default="Release {version}", help="Commit/tag message template."
    )
    args = ap.parse_args()

    ensure_git_repo()
    ensure_branch(args.branch)
    ensure_clean_working_tree()

    current = read_version_from_pyproject()
    if args.set_version:
        new = Version.parse(args.set_version)
    else:
        new = current.bump(args.part)

    tname = tag_name(new, args.tag_prefix)
    check_tag_does_not_exist(tname)

    print(f"Current version: {current}")
    print(f"New version:     {new}")
    print(f"Tag:             {tname}")

    run_checks(skip=args.skip_checks)

    if args.dry_run:
        print(
            "Dry-run enabled: no files will be modified, no git actions will be executed."
        )
        return 0

    # Bump version
    write_version_to_pyproject(new)

    # Commit
    msg = args.message.format(version=str(new))
    git("add", str(PYPROJECT))
    git("commit", "-m", msg)

    # Tag (annotated)
    git("tag", "-a", tname, "-m", msg)

    if not args.no_push:
        git("push", "origin", args.branch)
        git("push", "origin", tname)
    else:
        print("Skipping push (--no-push).")

    print("Release completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
