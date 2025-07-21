#!/usr/bin/env python3
"""Check for consistency between requirements.txt and pyproject.toml dependencies."""

import importlib
import sys
from sys import version_info
from typing import Any

tomllib: Any
if version_info >= (3, 11):
    tomllib = importlib.import_module("tomllib")
else:  # Python <3.11
    try:  # pragma: no cover - executed only for older versions
        tomllib = importlib.import_module("tomli")
    except ModuleNotFoundError:  # pragma: no cover - executed only if tomli missing
        sys.exit("Please install tomli: pip install tomli")


def parse_requirements(path: str = "requirements.txt") -> set[str]:
    reqs: set[str] = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split()[0]
            reqs.add(pkg)
    return reqs


def parse_pyproject(path: str = "pyproject.toml") -> set[str]:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    deps: set[str] = set()
    for entry in data.get("project", {}).get("dependencies", []):
        pkg = entry.split("==")[0].split(">=")[0].split("<=")[0].split()[0].strip("\"'")
        deps.add(pkg)
    return deps


def main() -> int:
    reqs = parse_requirements()
    deps = parse_pyproject()
    missing_in_py = reqs - deps
    missing_in_req = deps - reqs
    ok = True

    if missing_in_py:
        print(
            "Dependencies in requirements.txt missing in pyproject.toml:", missing_in_py
        )
        ok = False
    if missing_in_req:
        print(
            "Dependencies in pyproject.toml missing in requirements.txt:",
            missing_in_req,
        )
        ok = False

    if ok:
        print("✅ Requirements and pyproject.toml are consistent.")
        return 0
    print("❌ Inconsistencies detected.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
