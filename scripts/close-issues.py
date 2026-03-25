#!/usr/bin/env python3
"""Close a set of GitHub issues after a successful merge.

Reads the issue list from NDJSON on stdin (same format produced by
resolve-sub-issues.py) and closes every OPEN issue, including the parent.

Usage:
    close-issues.py <parent-issue-number> [owner/repo] < sub_issues.ndjson

    The parent issue is always closed regardless of what is in stdin.
    Each NDJSON line may have a "number" field; CLOSED issues are skipped.
    Pass an empty stdin (or /dev/null) to close only the parent.

Exit codes:
    0  all targeted issues closed successfully
    1  one or more issues failed to close (details printed to stderr)
"""

import json
import subprocess
import sys


def run_gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def gh_repo() -> str:
    result = run_gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    if result.returncode != 0:
        sys.exit(f"gh repo view failed: {result.stderr.strip()}")
    return result.stdout.strip()


def close_issue(number: int, repo: str) -> bool:
    result = run_gh("issue", "close", str(number), "--repo", repo)
    if result.returncode != 0:
        print(f"  FAILED #{number}: {result.stderr.strip()}", file=sys.stderr)
        return False
    print(f"  closed #{number}")
    return True


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} <parent-issue-number> [owner/repo]")

    try:
        parent = int(sys.argv[1])
    except ValueError:
        sys.exit(f"parent-issue-number must be an integer, got: {sys.argv[1]}")

    repo = sys.argv[2] if len(sys.argv) >= 3 else gh_repo()

    # Collect issue numbers from stdin (NDJSON from resolve-sub-issues.py)
    to_close: list[int] = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("state", "").upper() == "CLOSED":
            continue
        n = obj.get("number")
        if isinstance(n, int) and n != parent:
            to_close.append(n)

    # Always close sub-issues first, then the parent
    targets = to_close + [parent]

    print(f"Closing {len(targets)} issue(s) in {repo}: {targets}")
    failed = [n for n in targets if not close_issue(n, repo)]

    if failed:
        sys.exit(f"Failed to close issue(s): {failed}")


if __name__ == "__main__":
    main()
