#!/usr/bin/env python3
"""Check that every role defined in workflow.yml has its binary installed."""

import os
import shutil
import sys
from pathlib import Path

from workflow_utils import load_workflow, resolve

WORKFLOW_FILE = Path(os.environ.get(
    "WORKFLOW_FILE",
    Path(__file__).resolve().parent.parent / "workflow.yml",
))


def main() -> int:
    data = load_workflow(WORKFLOW_FILE)
    roles_map = resolve(data, "roles")
    if not isinstance(roles_map, dict):
        print("No roles defined in workflow.yml", file=sys.stderr)
        return 1

    role_names = sys.argv[1:] if len(sys.argv) > 1 else list(roles_map.keys())
    missing = 0

    for role in role_names:
        bin_name = resolve(data, f"roles.{role}.bin") or ""
        args = resolve(data, f"roles.{role}.args") or ""

        if not bin_name:
            print(f"MISS {role} binary is not configured", file=sys.stderr)
            missing += 1
            continue

        if shutil.which(bin_name):
            print(f"OK   {role} -> {bin_name} {args}")
        else:
            print(
                f"MISS {role} -> {bin_name} (install the binary or update workflow.yml)",
                file=sys.stderr,
            )
            missing += 1

    if missing:
        print(
            "Role validation failed. Fix the missing role binary in workflow.yml, "
            "then rerun this check.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
