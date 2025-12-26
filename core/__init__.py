"""Core system monitoring logic - platform agnostic."""

import time
import psutil
import logging

from core.config import CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, COOLDOWN

logger = logging.getLogger('monarx.core')


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
        logger.warning(f"High CPU usage detected: {stats['cpu']:.1f}%")
    if stats['mem'] >= MEM_LIMIT and can_notify('mem'):
        alerts.append(("High Memory", f"Memory at {stats['mem']:.1f}%"))
        logger.warning(f"High Memory usage detected: {stats['mem']:.1f}%")
    if stats['swap'] >= SWAP_LIMIT and can_notify('swap'):
        alerts.append(("High Swap", f"Swap at {stats['swap']:.1f}%"))
        logger.warning(f"High Swap usage detected: {stats['swap']:.1f}%")
    return alerts


def get_top_processes(by='cpu', limit=5):
    """
    Get top processes by CPU or memory usage.
    
    Args:
        by: 'cpu' or 'memory' (default: 'cpu')
        limit: Number of top processes to return (default: 5)
    
    Returns:
        List of tuples: (name, pid, usage_percent)
    """
    try:
        processes = []
        
        if by == 'cpu':
            # For CPU, get all processes and their CPU usage
            # Using interval=0 (non-blocking) - requires previous call to be accurate
            # On first call or if no previous measurement, we'll still get some processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    usage = proc.cpu_percent(interval=0)
                    # Include processes with CPU usage > 0
                    if usage > 0:
                        processes.append((
                            proc.info['name'],
                            proc.info['pid'],
                            usage
                        ))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # If no processes found, try one more time with a small interval
            # This helps on first call when there's no previous measurement
            if not processes:
                logger.debug("No CPU processes found with interval=0, trying with small interval...")
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        usage = proc.cpu_percent(interval=0.05)
                        if usage > 0:
                            processes.append((
                                proc.info['name'],
                                proc.info['pid'],
                                usage
                            ))
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
        else:  # memory
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    pinfo = proc.info
                    # Call memory_percent() as a method, not an info attribute
                    usage = proc.memory_percent()
                    # Skip processes with negligible memory
                    if usage >= 0.01:
                        processes.append((
                            pinfo['name'],
                            pinfo['pid'],
                            usage
                        ))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        
        # Sort by usage (descending) and return top N
        processes.sort(key=lambda x: x[2], reverse=True)
        result = processes[:limit]
        
        if result:
            top_process = result[0]
            logger.debug(f"Top {by} process: {top_process[0]} (PID: {top_process[1]}) - {top_process[2]:.1f}%")
        elif by == 'cpu':
            logger.debug("No CPU processes found (all may be at 0%)")
        
        return result
    except Exception as e:
        logger.error(f"Error getting top processes: {e}", exc_info=True)
        return []


def get_process_info(pid):
    """
    Get detailed information about a process.
    
    Args:
        pid: Process ID
    
    Returns:
        Dictionary with process info or None if process not found
    """
    try:
        proc = psutil.Process(pid)
        return {
            'name': proc.name(),
            'pid': pid,
            'cpu_percent': proc.cpu_percent(interval=0.1),
            'memory_percent': proc.memory_percent(),
            'memory_mb': proc.memory_info().rss / 1024 / 1024,
            'status': proc.status(),
            'create_time': proc.create_time(),
            'exe': proc.exe() if hasattr(proc, 'exe') else 'N/A',
            'cmdline': ' '.join(proc.cmdline()[:3]) if proc.cmdline() else 'N/A'
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

