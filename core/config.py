"""Monarx configuration and threshold persistence."""

import json
from pathlib import Path

__version__ = "1.0.0"

# Thresholds (percentage)
CPU_LIMIT = 85
MEM_LIMIT = 80
SWAP_LIMIT = 20

# Timing (seconds)
# CHECK_EVERY controls how often resource usage is sampled.
# Lower values (e.g. 5s) provide more responsive monitoring but increase CPU usage
# and power consumption, especially when this tool runs continuously.
# For production or battery-sensitive environments, consider using a higher value
# (e.g. 10–30 seconds) unless you specifically need near-real-time alerts.
CHECK_EVERY = 5
COOLDOWN = 120


def _config_file() -> Path:
    path = Path.home() / "Library" / "Application Support" / "Monarx"
    path.mkdir(parents=True, exist_ok=True)
    return path / "config.json"


def load_thresholds() -> tuple:
    """Load saved thresholds, falling back to defaults."""
    try:
        data = json.loads(_config_file().read_text())
        cpu = int(data.get('cpu_limit', CPU_LIMIT))
        mem = int(data.get('mem_limit', MEM_LIMIT))
        swap = int(data.get('swap_limit', SWAP_LIMIT))
        # Clamp to valid range
        return (
            max(1, min(100, cpu)),
            max(1, min(100, mem)),
            max(1, min(100, swap)),
        )
    except Exception:
        return CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT


def save_thresholds(cpu: int, mem: int, swap: int) -> None:
    """Persist threshold settings to disk."""
    try:
        _config_file().write_text(json.dumps(
            {'cpu_limit': cpu, 'mem_limit': mem, 'swap_limit': swap},
            indent=2
        ))
    except Exception:
        pass
