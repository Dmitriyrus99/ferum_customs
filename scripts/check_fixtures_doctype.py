#!/usr/bin/env python3
"""Pre-commit hook to verify fixture JSON contains 'doctype' field."""

import json
import sys
from pathlib import Path


def check_file(path: Path) -> bool:
    data = json.loads(path.read_text())
    missing = [str(i) for i, item in enumerate(data) if "doctype" not in item]
    if missing:
        print(f"{path}: missing 'doctype' in entries {', '.join(missing)}")
    return not missing


def main(paths: list[str]) -> int:
    ok = True
    for path_str in paths:
        path = Path(path_str)
        if path.suffix == ".json" and path.exists():
            if not check_file(path):
                ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
