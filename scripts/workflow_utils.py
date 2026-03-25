"""Shared utilities for reading and resolving workflow.yml."""

import sys
from pathlib import Path
from typing import Any, Optional

import yaml


def default_workflow_path() -> Path:
    """Return the default workflow.yml path relative to the scripts directory."""
    return Path(__file__).resolve().parent.parent / "workflow.yml"


def load_workflow(path: Optional[Path] = None) -> dict:
    """Load and parse workflow.yml, returning the top-level dict."""
    if path is None:
        path = default_workflow_path()
    with open(path) as f:
        return yaml.safe_load(f)


def resolve(data: Any, key_path: str) -> Any:
    """Resolve a dotted key path (e.g. 'roles.implementer.bin') against a dict."""
    for key in key_path.split("."):
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return None
    return data
