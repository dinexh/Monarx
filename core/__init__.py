"""Core system monitoring logic - platform agnostic."""

import time
import psutil
import logging
import subprocess
import os
import sys
import gc

from core.config import CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, COOLDOWN

logger = logging.getLogger('monarx.core')

# Cache constant values to avoid repeated subprocess calls
_PAGE_SIZE = None

def get_page_size():
    global _PAGE_SIZE
    if _PAGE_SIZE is None:
        try:
            _PAGE_SIZE = int(subprocess.check_output(['pagesize']).strip())
        except Exception:
            _PAGE_SIZE = 4096  # Fallback
    return _PAGE_SIZE

def get_macos_memory_info():
    """Get detailed macOS memory breakdown."""
    if sys.platform != 'darwin':
        return None
    
    try:
        page_size = get_page_size()
        
        # Get vm_stat - fast call
        vm_stat = subprocess.check_output(['vm_stat']).decode('utf-8')
        stats = {}
        for line in vm_stat.split('\n'):
            if ':' in line:
                try:
                    key, val = line.split(':')
                    if 'Mach Virtual Memory Statistics' in key:
                        continue
                    stats[key.strip()] = int(val.strip().strip('.')) * page_size
                except (ValueError, IndexError):
                    continue
        
        # Get memory_pressure for compressed info - slightly slower but provides critical data
        try:
            mp_output = subprocess.check_output(['memory_pressure'], stderr=subprocess.STDOUT).decode('utf-8')
            compressed_bytes = 0
            for line in mp_output.split('\n'):
                if 'Pages used by compressor:' in line:
                    compressed_bytes = int(line.split(':')[1].strip()) * page_size
                    break
        except Exception:
            compressed_bytes = 0

        wired = stats.get('Pages wired down', 0)
        active = stats.get('Pages active', 0)
        inactive = stats.get('Pages inactive', 0)
        speculative = stats.get('Pages speculative', 0)
        
        return {
            'wired': wired / (1024**3),
            'active': active / (1024**3),
            'compressed': compressed_bytes / (1024**3),
            'cached': (inactive + speculative) / (1024**3)
        }
    except Exception as e:
        logger.error(f"Error getting macOS memory breakdown: {e}")
        return None

def get_memory_pressure():
    """Get macOS memory pressure level - very fast sysctl call."""
    if sys.platform != 'darwin':
        return "N/A", 0
    
    try:
        pressure_val = int(subprocess.check_output(['sysctl', '-n', 'vm.memory_pressure']).strip())
        status = "OK"
        if pressure_val == 1:
            status = "WARN"
        elif pressure_val >= 2:
            status = "HIGH"
        return status, pressure_val
    except Exception as e:
        logger.error(f"Error getting memory pressure: {e}")
        return "UNKNOWN", 0

def get_stats():
    """Get current CPU, memory, and swap usage."""
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    stats = {
        'cpu': psutil.cpu_percent(interval=None), # Non-blocking for background efficiency
        'mem': vm.percent,
        'swap': swap.percent,
        'mem_total_gb': vm.total / (1024**3),
    }
    
    if sys.platform == 'darwin':
        stats['macos_mem'] = get_macos_memory_info()
        stats['pressure_status'], stats['pressure_val'] = get_memory_pressure()
        
        # Simple lag risk check
        if stats['macos_mem']:
            m = stats['macos_mem']
            stats['lag_risk'] = m['compressed'] > m['active'] or stats['pressure_val'] > 0
        else:
            stats['lag_risk'] = False
            
    # Trigger lightweight GC occasionally
    if time.time() % 60 < 5: # Roughly every minute
        gc.collect(1) # Generation 1 collect is fast
        
    return stats

def get_combined_process_info(limit=5):
    """
    Combined pass to get top CPU, Top Memory, and GPU-heavy processes.
    This is much more efficient than multiple passes.
    """
    if sys.platform != 'darwin':
        return [], [], []

    cpu_procs = []
    mem_procs = []
    gpu_heavy_names = {'Electron', 'WebKit', 'Google Chrome', 'Slack', 'Discord', 'WindowServer', 'Helper'}
    gpu_found = []

    try:
        # One pass over all processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                name = info['name']
                pid = info['pid']
                cpu = info.get('cpu_percent')
                mem = info.get('memory_percent')

                # Handle potential None values
                if cpu is None: cpu = 0.0
                if mem is None: mem = 0.0

                # Tag process characteristics
                labels = []
                if name and any(s in name.lower() for s in ['mds', 'mdworker']):
                    labels.append("Spotlight")
                
                is_gpu_heavy = name and any(h in name for h in gpu_heavy_names)
                if is_gpu_heavy:
                    labels.append("GPU")

                label_str = f" [{', '.join(labels)}]" if labels else ""
                proc_data = {
                    'name': f"{name}{label_str}" if name else f"PID {pid}",
                    'raw_name': name or f"PID {pid}",
                    'pid': pid,
                    'cpu': cpu,
                    'mem': mem
                }

                if cpu > 0.1:
                    cpu_procs.append(proc_data)
                if mem > 0.1:
                    mem_procs.append(proc_data)
                if is_gpu_heavy and len(gpu_found) < 3:
                    gpu_found.append(proc_data)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort and limit
        cpu_procs.sort(key=lambda x: x['cpu'], reverse=True)
        mem_procs.sort(key=lambda x: x['mem'], reverse=True)
        
        return cpu_procs[:limit], mem_procs[:limit], gpu_found[:3]

    except Exception as e:
        logger.error(f"Error in combined process scan: {e}")
        return [], [], []


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
    
    # Generic thresholds
    if stats['cpu'] >= CPU_LIMIT and can_notify('cpu'):
        alerts.append(("High CPU", f"CPU at {stats['cpu']:.1f}%"))
        
    if stats['mem'] >= MEM_LIMIT and can_notify('mem'):
        alerts.append(("High Memory", f"Memory at {stats['mem']:.1f}%"))
        
    if stats['swap'] >= SWAP_LIMIT and can_notify('swap'):
        alerts.append(("High Swap", f"Swap at {stats['swap']:.1f}%"))

    # macOS specific alerts
    if sys.platform == 'darwin':
        if stats.get('pressure_status') in ['WARN', 'HIGH'] and can_notify('pressure'):
            alerts.append(("Memory Pressure", f"Status: {stats['pressure_status']}"))
            
        if stats.get('lag_risk') and can_notify('lag_risk'):
            alerts.append(("Lag Risk Detected", "Compressed Memory > Active Memory"))

    return alerts

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

