from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path


def collect_environment() -> dict[str, str]:
    """Capture enough context to reproduce a run and triage failures."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=Path(__file__).resolve().parents[1],
            check=True, capture_output=True, text=True, timeout=2,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = "unavailable"
    return {"python": sys.version.split()[0], "platform": platform.platform(),
            "machine": platform.machine(), "git_commit": commit}
