#!/usr/bin/env python3.8
"""Pre-commit hook to verify fixture JSON contains 'doctype' field."""

import json
import sys
from pathlib import Path
from typing import List


def check_file(path: Path) -> bool:
    """Check if the JSON file at the given path contains 'doctype' in all entries."""
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        print(f"{path}: invalid JSON")
        return False

    missing = [str(i) for i, item in enumerate(data) if "doctype" not in item]
    if missing:
        print(f"{path}: missing 'doctype' in entries {', '.join(missing)}")
    return not missing


def main(paths: List[str]) -> int:
    """Main function to check multiple JSON files for 'doctype' field."""
    ok = True
    for path_str in paths:
        path = Path(path_str)
        if path.suffix == ".json" and path.exists():
            if not check_file(path):
                ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
