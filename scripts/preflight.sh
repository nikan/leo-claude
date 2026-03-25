#!/usr/bin/env bash
# Thin launcher that ensures Python 3 + PyYAML are available, then
# hands off to the real preflight check written in Python.
#
# This is the only bash script in the project. It exists because
# check-environment.py cannot check for its own interpreter.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Locate a Python 3 interpreter -----------------------------------
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    # Verify it is actually Python 3
    if "$candidate" -c "import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)" 2>/dev/null; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "ERROR: Python 3 is required but was not found." >&2
  echo "" >&2
  case "$(uname -s)" in
    Darwin)
      echo "  Install with Homebrew:  brew install python3" >&2
      echo "  Or download from:       https://www.python.org/downloads/macos/" >&2
      ;;
    Linux)
      echo "  Debian/Ubuntu:  sudo apt install python3 python3-pip" >&2
      echo "  Fedora/RHEL:    sudo dnf install python3 python3-pip" >&2
      echo "  Arch:           sudo pacman -S python" >&2
      ;;
    MINGW*|MSYS*|CYGWIN*)
      echo "  Download from:  https://www.python.org/downloads/windows/" >&2
      echo "  Or use winget:  winget install Python.Python.3.12" >&2
      echo "  Or use scoop:   scoop install python" >&2
      ;;
    *)
      echo "  Download from:  https://www.python.org/downloads/" >&2
      ;;
  esac
  exit 1
fi

# --- Check for PyYAML -------------------------------------------------
if ! "$PYTHON" -c "import yaml" 2>/dev/null; then
  echo "ERROR: The PyYAML package is required but not installed." >&2
  echo "" >&2
  echo "  Install with:  $PYTHON -m pip install pyyaml" >&2
  exit 1
fi

# --- Hand off to the Python preflight script ---------------------------
exec "$PYTHON" "${SCRIPT_DIR}/check-environment.py" "$@"
