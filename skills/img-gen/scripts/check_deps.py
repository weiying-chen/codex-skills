#!/usr/bin/env python3
import importlib
import sys

REQUIRED = [
    ("PIL", "pillow"),
]


def main() -> int:
    missing = []
    for module_name, package_name in REQUIRED:
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(package_name)

    if not missing:
        print("Dependency check passed")
        return 0

    unique = sorted(set(missing))
    print("Missing Python dependencies: " + ", ".join(unique), file=sys.stderr)
    print("Install with:", file=sys.stderr)
    print("  pip install -r requirements.txt", file=sys.stderr)
    print("or", file=sys.stderr)
    print("  uv pip install -r requirements.txt", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
