#!/usr/bin/env python3
"""Read a dotted key path from workflow.yml and print the value.

Usage:
    read-workflow.py <key-path> [workflow-file]

Examples:
    read-workflow.py branches.target_base
    read-workflow.py roles.implementer.bin
    read-workflow.py preflight.required_tools   # prints one item per line
"""

import sys
from pathlib import Path

from workflow_utils import load_workflow, resolve


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <key-path> [workflow-file]", file=sys.stderr)
        sys.exit(1)

    key_path = sys.argv[1]
    workflow_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    data = load_workflow(workflow_file)
    value = resolve(data, key_path)

    if value is None:
        print(f"Key not found: {key_path}", file=sys.stderr)
        sys.exit(1)
    elif isinstance(value, list):
        for item in value:
            print(item)
    elif isinstance(value, dict):
        for k in value:
            print(k)
    else:
        print(value)


if __name__ == "__main__":
    main()
