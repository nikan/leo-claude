#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
READ_WF="${SCRIPT_DIR}/read-workflow.py"
WORKFLOW_FILE="${WORKFLOW_FILE:-${SCRIPT_DIR}/../workflow.yml}"

if [[ ! -f "${WORKFLOW_FILE}" ]]; then
  echo "Missing workflow definition: ${WORKFLOW_FILE}" >&2
  exit 1
fi

missing=0

check_bin() {
  local bin_name="$1"
  if command -v "${bin_name}" >/dev/null 2>&1; then
    printf 'OK   %s\n' "${bin_name}"
  else
    printf 'MISS %s\n' "${bin_name}" >&2
    missing=1
  fi
}

echo "Checking baseline CLI dependencies..."
while IFS= read -r tool; do
  check_bin "${tool}"
done < <(python3 "${READ_WF}" preflight.required_tools "${WORKFLOW_FILE}")

echo
echo "Checking repository state..."
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  printf 'OK   %s\n' "git repository detected"
else
  printf 'MISS %s\n' "git repository detected" >&2
  missing=1
fi

echo
echo "Checking configured defaults..."
target_base="$(python3 "${READ_WF}" branches.target_base "${WORKFLOW_FILE}" 2>/dev/null || true)"
if [[ -n "${target_base}" ]]; then
  printf 'OK   target_base=%s\n' "${target_base}"
else
  printf 'MISS branches.target_base is empty\n' >&2
  missing=1
fi

merge_method="$(python3 "${READ_WF}" branches.merge_method "${WORKFLOW_FILE}" 2>/dev/null || true)"
if [[ -n "${merge_method}" ]]; then
  printf 'OK   merge_method=%s\n' "${merge_method}"
else
  printf 'MISS branches.merge_method is empty\n' >&2
  missing=1
fi

echo
echo "Checking GitHub auth status..."
if gh auth status >/dev/null 2>&1; then
  printf 'OK   %s\n' "gh auth status"
else
  printf 'MISS %s\n' "gh auth status" >&2
  missing=1
fi

echo
echo "Checking vibe auth status..."
if [[ -f "${HOME}/.vibe/.env" ]] && grep -q 'MISTRAL_API_KEY' "${HOME}/.vibe/.env" 2>/dev/null; then
  if echo "" | timeout 15 vibe -p "Say OK" --output text >/dev/null 2>&1; then
    printf 'OK   %s\n' "vibe auth (API key valid)"
  else
    printf 'MISS %s\n' "vibe auth (key found but API call failed)" >&2
    missing=1
  fi
else
  printf 'MISS %s\n' "vibe auth (run: vibe --setup)" >&2
  missing=1
fi

echo
echo "Checking configured role binaries..."
if ! "${SCRIPT_DIR}/check-role-installation.sh"; then
  missing=1
fi

if [[ ${missing} -ne 0 ]]; then
  echo
  echo "Environment check failed. Remediate the reported problem, then rerun this check before continuing." >&2
  exit 1
fi

echo
echo "Environment check passed."
