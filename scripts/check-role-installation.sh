#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
READ_WF="${SCRIPT_DIR}/read-workflow.py"
WORKFLOW_FILE="${WORKFLOW_FILE:-${SCRIPT_DIR}/../workflow.yml}"

if [[ ! -f "${WORKFLOW_FILE}" ]]; then
  echo "Missing workflow definition: ${WORKFLOW_FILE}" >&2
  exit 1
fi

# Get role names from workflow.yml (roles map keys)
roles=($(python3 "${READ_WF}" roles "${WORKFLOW_FILE}"))

if [[ $# -gt 0 ]]; then
  roles=("$@")
fi

missing=0

for role in "${roles[@]}"; do
  bin="$(python3 "${READ_WF}" "roles.${role}.bin" "${WORKFLOW_FILE}" 2>/dev/null || true)"
  args="$(python3 "${READ_WF}" "roles.${role}.args" "${WORKFLOW_FILE}" 2>/dev/null || true)"

  if [[ -z "${bin}" ]]; then
    printf 'MISS %s binary is not configured\n' "${role}" >&2
    missing=1
    continue
  fi

  if command -v "${bin}" >/dev/null 2>&1; then
    printf 'OK   %s -> %s %s\n' "${role}" "${bin}" "${args}"
  else
    printf 'MISS %s -> %s (install the binary or update workflow.yml)\n' "${role}" "${bin}" >&2
    missing=1
  fi
done

if [[ ${missing} -ne 0 ]]; then
  echo "Role validation failed. Fix the missing role binary in workflow.yml, then rerun this check." >&2
  exit 1
fi
