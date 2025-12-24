"""Core system monitoring logic - platform agnostic."""

import time
import psutil

from config import CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, COOLDOWN


def get_stats():
    """Get current CPU, memory, and swap usage."""
    return {
        'cpu': psutil.cpu_percent(interval=0.1),
        'mem': psutil.virtual_memory().percent,
        'swap': psutil.swap_memory().percent
    }


def get_status(value, limit, warn_factor=0.85):
    """Get status label based on value and limit."""
    warn_threshold = limit * warn_factor
    if value >= limit:
        return "HIGH"
    if value >= warn_threshold:
        return "WARN"
    return "OK"


# Notification cooldown tracking
_last_alert = {}


def can_notify(key):
    """Check if notification can be sent (respects cooldown)."""
    now = time.time()
    if key not in _last_alert or now - _last_alert[key] > COOLDOWN:
        _last_alert[key] = now
        return True
    return False


def check_thresholds(stats):
    """Check if any thresholds are exceeded. Returns list of alerts."""
    alerts = []
    if stats['cpu'] >= CPU_LIMIT and can_notify('cpu'):
        alerts.append(("High CPU", f"CPU at {stats['cpu']:.1f}%"))
    if stats['mem'] >= MEM_LIMIT and can_notify('mem'):
        alerts.append(("High Memory", f"Memory at {stats['mem']:.1f}%"))
    if stats['swap'] >= SWAP_LIMIT and can_notify('swap'):
        alerts.append(("High Swap", f"Swap at {stats['swap']:.1f}%"))
    return alerts
