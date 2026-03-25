#!/usr/bin/env python3
"""Resolve sub-issues for a GitHub epic/parent issue.

Checks two sources, in priority order:
  1. GitHub native sub-issues  (GraphQL `subIssues` field)
  2. Task-list body references  (lines matching `- [x] #N` or `- [ ] #N`)

Usage:
    resolve-sub-issues.py <issue-number> [owner/repo]

    If owner/repo is omitted it is inferred from `gh repo view`.

Output (stdout): one JSON object per line (NDJSON), each with fields:
    number   int
    title    str
    state    "OPEN" | "CLOSED"
    source   "sub_issue" | "task_list"
    url      str

Exit codes:
    0  success (even if zero sub-issues found)
    1  bad arguments or gh/GraphQL error
"""

import json
import re
import subprocess
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
    )


def gh_repo() -> str:
    """Return 'owner/repo' for the current directory."""
    result = run_gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    if result.returncode != 0:
        sys.exit(f"gh repo view failed: {result.stderr.strip()}")
    return result.stdout.strip()


def graphql(query: str, variables: dict) -> dict:
    """Run a GraphQL query by piping JSON to `gh api graphql --input -`."""
    payload = json.dumps({"query": query, "variables": variables})
    result = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=payload,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


# ---------------------------------------------------------------------------
# Strategy 1 — native GitHub sub-issues (GraphQL subIssues field)
# ---------------------------------------------------------------------------

_SUB_ISSUES_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      subIssues(first: 100) {
        nodes {
          number
          title
          state
          url
        }
      }
    }
  }
}
"""


def fetch_sub_issues(owner: str, repo: str, number: int) -> list[dict]:
    data = graphql(_SUB_ISSUES_QUERY, {"owner": owner, "repo": repo, "number": number})
    try:
        nodes = (
            data["data"]["repository"]["issue"]["subIssues"]["nodes"]
        )
        return [
            {
                "number": n["number"],
                "title": n["title"],
                "state": n["state"],
                "source": "sub_issue",
                "url": n["url"],
            }
            for n in nodes
        ]
    except (KeyError, TypeError):
        return []


# ---------------------------------------------------------------------------
# Strategy 2 — task-list body references
# ---------------------------------------------------------------------------

_ISSUE_BODY_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      body
    }
  }
}
"""

# Matches GitHub task-list lines:  - [ ] #42  or  - [x] #42
_TASK_RE = re.compile(r"^- \[[ xX]\] #(\d+)", re.MULTILINE)
# Also matches full GitHub issue URLs in task lines
_TASK_URL_RE = re.compile(
    r"^- \[[ xX]\] https://github\.com/[^/]+/[^/]+/issues/(\d+)",
    re.MULTILINE,
)


def fetch_issue_details(owner: str, repo: str, number: int) -> dict:
    result = run_gh(
        "issue", "view", str(number),
        "--repo", f"{owner}/{repo}",
        "--json", "number,title,state,url",
    )
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def fetch_task_list_issues(owner: str, repo: str, number: int) -> list[dict]:
    data = graphql(_ISSUE_BODY_QUERY, {"owner": owner, "repo": repo, "number": number})
    try:
        body = data["data"]["repository"]["issue"]["body"] or ""
    except (KeyError, TypeError):
        return []

    numbers = {int(m) for m in _TASK_RE.findall(body)}
    numbers |= {int(m) for m in _TASK_URL_RE.findall(body)}

    results = []
    for n in sorted(numbers):
        details = fetch_issue_details(owner, repo, n)
        if details:
            results.append(
                {
                    "number": details["number"],
                    "title": details["title"],
                    "state": details["state"],
                    "source": "task_list",
                    "url": details["url"],
                }
            )
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} <issue-number> [owner/repo]")

    try:
        issue_number = int(sys.argv[1])
    except ValueError:
        sys.exit(f"issue-number must be an integer, got: {sys.argv[1]}")

    if len(sys.argv) >= 3:
        owner, _, repo = sys.argv[2].partition("/")
        if not repo:
            sys.exit("owner/repo must be in 'owner/repo' format")
    else:
        slug = gh_repo()
        owner, _, repo = slug.partition("/")

    # Strategy 1: native sub-issues
    sub_issues = fetch_sub_issues(owner, repo, issue_number)

    # Strategy 2: task-list body — only add issues not already found above
    known = {i["number"] for i in sub_issues}
    task_issues = [
        i for i in fetch_task_list_issues(owner, repo, issue_number)
        if i["number"] not in known
    ]

    all_issues = sub_issues + task_issues

    if not all_issues:
        print(f"No sub-issues found for #{issue_number}", file=sys.stderr)

    for issue in all_issues:
        print(json.dumps(issue))


if __name__ == "__main__":
    main()
