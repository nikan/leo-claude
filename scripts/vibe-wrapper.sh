#!/usr/bin/env bash
# Wrapper for vibe that ensures its log directory is writable before invoking.
#
# Strategy 1 (primary): create ~/.vibe/logs/ and verify the log file is
#   writable, then exec vibe normally.
# Strategy 2 (fallback): redirect HOME to a temp dir and copy .env into it,
#   so vibe gets a fully writable home without losing API key config.
#   Confirmed working: vibe starts cleanly when HOME=/tmp/vibe-home.

set -euo pipefail

LOG_DIR="${HOME}/.vibe/logs"
LOG_FILE="${LOG_DIR}/vibe.log"

if mkdir -p "${LOG_DIR}" 2>/dev/null && touch "${LOG_FILE}" 2>/dev/null; then
    exec vibe "$@"
fi

# Fallback: writable temp HOME
VIBE_HOME="$(mktemp -d /tmp/vibe-home-XXXXXX)"
trap 'rm -rf "${VIBE_HOME}"' EXIT

mkdir -p "${VIBE_HOME}/.vibe/logs"
if [ -f "${HOME}/.vibe/.env" ]; then
    cp "${HOME}/.vibe/.env" "${VIBE_HOME}/.vibe/.env"
fi

exec env HOME="${VIBE_HOME}" vibe "$@"
