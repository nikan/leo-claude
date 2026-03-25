#!/usr/bin/env python3
"""Cross-platform preflight environment check for the leo-claude workflow."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from workflow_utils import load_workflow, resolve

SCRIPT_DIR = Path(__file__).resolve().parent
WORKFLOW_FILE = Path(os.environ.get(
    "WORKFLOW_FILE",
    SCRIPT_DIR.parent / "workflow.yml",
))

missing = 0


def ok(label: str) -> None:
    print(f"OK   {label}")


def miss(label: str) -> None:
    global missing
    print(f"MISS {label}", file=sys.stderr)
    missing += 1


def check_bin(name: str) -> None:
    if shutil.which(name):
        ok(name)
    else:
        miss(name)


def check_baseline_tools(data: dict) -> None:
    print("Checking baseline CLI dependencies...")
    tools = resolve(data, "preflight.required_tools") or []
    for tool in tools:
        check_bin(tool)


def check_repo() -> None:
    print()
    print("Checking repository state...")
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
    )
    if result.returncode == 0:
        ok("git repository detected")
    else:
        miss("git repository detected")


def check_defaults(data: dict) -> None:
    print()
    print("Checking configured defaults...")

    target_base = resolve(data, "branches.target_base") or ""
    if target_base:
        ok(f"target_base={target_base}")
    else:
        miss("branches.target_base is empty")

    merge_method = resolve(data, "branches.merge_method") or ""
    if merge_method:
        ok(f"merge_method={merge_method}")
    else:
        miss("branches.merge_method is empty")


def check_gh_auth() -> None:
    print()
    print("Checking GitHub auth status...")
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
    )
    if result.returncode == 0:
        ok("gh auth status")
    else:
        miss("gh auth status")


def check_vibe_auth() -> None:
    print()
    print("Checking vibe auth status...")

    env_file = Path.home() / ".vibe" / ".env"
    if not env_file.exists():
        miss("vibe auth (run: vibe --setup)")
        return

    try:
        contents = env_file.read_text()
    except OSError:
        miss("vibe auth (cannot read ~/.vibe/.env)")
        return

    if "MISTRAL_API_KEY" not in contents:
        miss("vibe auth (MISTRAL_API_KEY not found in ~/.vibe/.env)")
        return

    try:
        result = subprocess.run(
            ["vibe", "-p", "Say OK", "--output", "text"],
            input="",
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            ok("vibe auth (API key valid)")
        else:
            miss("vibe auth (key found but API call failed)")
    except FileNotFoundError:
        miss("vibe auth (vibe binary not found)")
    except subprocess.TimeoutExpired:
        miss("vibe auth (API call timed out)")


def check_roles() -> None:
    print()
    print("Checking configured role binaries...")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "check-role-installation.py")],
        capture_output=False,
    )
    if result.returncode != 0:
        global missing
        missing += 1


def main() -> int:
    if not WORKFLOW_FILE.exists():
        print(f"Missing workflow definition: {WORKFLOW_FILE}", file=sys.stderr)
        return 1

    data = load_workflow(WORKFLOW_FILE)

    check_baseline_tools(data)
    check_repo()
    check_defaults(data)
    check_gh_auth()
    check_vibe_auth()
    check_roles()

    if missing:
        print()
        print(
            "Environment check failed. Remediate the reported problem, "
            "then rerun this check before continuing.",
            file=sys.stderr,
        )
        return 1

    print()
    print("Environment check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
