"""Monarx - macOS menu bar implementation."""

import sys
import logging
import rumps

from core.config import CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, CHECK_EVERY
from core import get_stats, get_status, check_thresholds, get_combined_process_info, can_notify
from core.logging import setup_logging

logger = logging.getLogger('monarx.mac')


def setup_macos():
    """Setup macOS-specific behavior."""
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    logger.info("macOS activation policy set to accessory (no Dock icon)")


def notify(title, message, subtitle=""):
    """Send a macOS notification with optional subtitle.
    
    Uses osascript for reliable notifications on modern macOS versions
    (Ventura, Sonoma, Sequoia) since NSUserNotification is deprecated.
    """
    import subprocess
    
    def escape_applescript(text):
        """Escape special characters for AppleScript strings."""
        # Escape backslashes first, then quotes
        return text.replace('\\', '\\\\').replace('"', '\\"')
    
    try:
        # Escape all text for AppleScript
        safe_title = escape_applescript(str(title))
        safe_message = escape_applescript(str(message))
        safe_subtitle = escape_applescript(str(subtitle)) if subtitle else ""
        
        # Build the osascript command for display notification
        script = f'display notification "{safe_message}" with title "{safe_title}"'
        if safe_subtitle:
            script += f' subtitle "{safe_subtitle}"'
        script += ' sound name "default"'
        
        subprocess.run(
            ['osascript', '-e', script],
            check=True,
            capture_output=True,
            timeout=5
        )
        logger.info(f"Notification sent: {title} - {subtitle} - {message}")
    except subprocess.TimeoutExpired:
        logger.warning(f"Notification timed out: {title} - {message}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to send notification: {e}")
        # Fallback to rumps notification in case osascript fails
        try:
            rumps.notification(title, subtitle, message)
            logger.info(f"Fallback notification sent via rumps: {title}")
        except Exception as fallback_error:
            logger.error(f"Fallback notification also failed: {fallback_error}")


def get_status_label(status):
    """Get text label for status."""
    labels = {
        "OK": "NORMAL",
        "WARN": "WARN",
        "HIGH": "CRITICAL"
    }
    return labels.get(status, "IDLE")


def get_progress_bar(percent, width=10):
    """Create a simple ASCII progress bar."""
    filled = int(percent / 100 * width)
    return "[" + "■" * filled + "□" * (width - filled) + "]"


def format_process_name(name, max_length=28):
    """Format process name with smart truncation."""
    if len(name) <= max_length:
        return name
    # Try to preserve file extension
    if '.' in name:
        parts = name.rsplit('.', 1)
        if len(parts) == 2:
            ext = parts[1]
            max_base = max_length - len(ext) - 1
            return f"{name[:max_base]}….{ext}"
    return name[:max_length-1] + "…"


class MonarxApp(rumps.App):
    """Menu bar application for system monitoring."""
    
    def __init__(self):
        super().__init__(name="Monarx", title="Loading...", quit_button=None)
        self.top_cpu_processes = []
        self.top_mem_processes = []
        self.current_stats = {}
        self._menu_updating = False
        
        # Dynamic thresholds
        self.cpu_limit = CPU_LIMIT
        self.mem_limit = MEM_LIMIT
        self.swap_limit = SWAP_LIMIT
        
        self._build_menu()
        logger.info("Monarx app initialized")
    
    def _build_menu(self):
        """Build the dropdown menu."""
        # Initial placeholders
        self.menu = [
            rumps.MenuItem("SYSTEM MONITOR", callback=None),
            None,
            "Loading details...",
            None,
            rumps.MenuItem("SETTINGS", callback=None),
            rumps.MenuItem("  Change Thresholds", callback=self._change_thresholds),
            None,
            rumps.MenuItem("REFRESH", callback=self._refresh),
            rumps.MenuItem("VIEW LOGS", callback=self._view_logs),
            None,
            rumps.MenuItem("QUIT", callback=self._quit)
        ]
    
    def _change_thresholds(self, _):
        """Change monitoring thresholds."""
        response = rumps.Window(
            message=f"Current: CPU={self.cpu_limit}%, Mem={self.mem_limit}%, Swap={self.swap_limit}%\n"
                    f"Enter new values as 'CPU MEM SWAP' (e.g., '90 85 30'):",
            title="Update Thresholds",
            cancel=True
        ).run()
        
        if response.clicked:
            try:
                vals = response.text.split()
                if len(vals) == 3:
                    self.cpu_limit = int(vals[0])
                    self.mem_limit = int(vals[1])
                    self.swap_limit = int(vals[2])
                    notify("Monarx", "Thresholds updated")
                    logger.info(f"Thresholds updated: CPU={self.cpu_limit}, Mem={self.mem_limit}, Swap={self.swap_limit}")
                    self._update(None)
            except Exception as e:
                rumps.alert("Invalid input. Please enter three numbers.")
                logger.error(f"Error updating thresholds: {e}")

    def _kill_process(self, sender):
        """Kill a process."""
        pid = sender.pid
        name = sender.proc_name
        try:
            import os
            import signal
            os.kill(pid, signal.SIGTERM)
            notify("Monarx", f"Sent SIGTERM to {name} (PID: {pid})")
            logger.info(f"Killed process {name} (PID: {pid})")
            self._update(None)
        except Exception as e:
            notify("Monarx", f"Failed to kill {name}: {e}")
            logger.error(f"Error killing process {pid}: {e}")

    def _open_process_info(self, sender):
        """Show process info (placeholder for more advanced action)."""
        pid = sender.pid
        notify("Monarx", f"Process PID: {pid}")
        # Could use 'open' or similar to show in Activity Monitor if we knew how to focus it on a PID
        import subprocess
        subprocess.run(['open', '-a', 'Activity Monitor'])

    def _update_process_menu(self):
        """Update the top processes menu items."""
        if self._menu_updating:
            return
        self._menu_updating = True
        
        try:
            stats = self.current_stats
            if not stats:
                return

            # Get combined process info in one pass - much more efficient
            cpu_procs, mem_procs, gpu_procs = get_combined_process_info(limit=5)
            
            # Health Summary
            pressure_label = get_status_label(stats.get('pressure_status', 'OK'))
            lag_state = "STRESSED" if stats.get('lag_risk') else "HEALTHY"
            
            summary_title = f"System Health: {pressure_label} Pressure | {lag_state}"
            
            # Memory Breakdown
            m = stats.get('macos_mem', {})
            mem_breakdown = []
            if m:
                mem_breakdown = [
                    rumps.MenuItem(f"RAM Usage {get_progress_bar(stats['mem'])} {stats['mem']:.1f}%"),
                    rumps.MenuItem(f"  + Wired: {m.get('wired', 0):.1f} GB"),
                    rumps.MenuItem(f"  + Active: {m.get('active', 0):.1f} GB"),
                    rumps.MenuItem(f"  + Compressed: {m.get('compressed', 0):.1f} GB {'(HIGH)' if m.get('compressed', 0) > m.get('active', 0) else ''}"),
                    rumps.MenuItem(f"  + Cached: {m.get('cached', 0):.1f} GB"),
                ]
            
            # GPU Info - Heuristic based from combined pass
            gpu_activity = "IDLE"
            if gpu_procs:
                total_gpu_cpu = sum(p['cpu'] for p in gpu_procs)
                if total_gpu_cpu > 50:
                    gpu_activity = "HEAVY"
                elif total_gpu_cpu > 10:
                    gpu_activity = "MODERATE"
            
            gpu_title = f"GPU Activity: {gpu_activity}"
            
            menu_items = [
                rumps.MenuItem(summary_title),
                None,
                rumps.MenuItem(f"CPU Load {get_progress_bar(stats['cpu'])} {stats['cpu']:.1f}% ({get_status_label(get_status(stats['cpu'], self.cpu_limit))})"),
                rumps.MenuItem(gpu_title),
                None,
            ]
            
            menu_items.extend(mem_breakdown)
            menu_items.append(rumps.MenuItem(f"Swap Usage {get_progress_bar(stats['swap'])} {stats['swap']:.1f}%"))
            menu_items.append(None)
            
            # Thresholds display
            menu_items.extend([
                rumps.MenuItem("SETTINGS"),
                rumps.MenuItem(f"  Thresholds: CPU {self.cpu_limit}% | MEM {self.mem_limit}% | SWAP {self.swap_limit}%", callback=self._change_thresholds),
                None,
            ])
            
            # CPU Processes
            menu_items.append(rumps.MenuItem("TOP CPU PROCESSES:"))
            for p in cpu_procs:
                p_item = rumps.MenuItem(f"  {p['name'][:25]}: {p['cpu']:.1f}%")
                kill_item = rumps.MenuItem("Kill Process", callback=self._kill_process)
                kill_item.pid = p['pid']
                kill_item.proc_name = p['raw_name']
                info_item = rumps.MenuItem("Show PID", callback=self._open_process_info)
                info_item.pid = p['pid']
                
                p_item.add(kill_item)
                p_item.add(info_item)
                menu_items.append(p_item)
            
            menu_items.append(None)
            
            # Memory Processes
            menu_items.append(rumps.MenuItem("TOP MEMORY PROCESSES:"))
            for p in mem_procs:
                p_item = rumps.MenuItem(f"  {p['name'][:25]}: {p['mem']:.1f}%")
                kill_item = rumps.MenuItem("Kill Process", callback=self._kill_process)
                kill_item.pid = p['pid']
                kill_item.proc_name = p['raw_name']
                
                p_item.add(kill_item)
                menu_items.append(p_item)
            
            # Standard items
            menu_items.extend([
                None,
                rumps.MenuItem("REFRESH", callback=self._refresh),
                rumps.MenuItem("VIEW LOGS", callback=self._view_logs),
                rumps.MenuItem("QUIT", callback=self._quit)
            ])
            
            # Clear and set menu
            try:
                if hasattr(self, '_menu') and self._menu:
                    ns_menu = self._menu._menu
                    if ns_menu:
                        ns_menu.removeAllItems()
            except Exception:
                pass
            
            self.menu = menu_items
        finally:
            self._menu_updating = False
    
    @rumps.timer(CHECK_EVERY)
    def _update(self, _):
        """Update stats on timer."""
        try:
            stats = get_stats()
            self.current_stats = stats
            
            # Dynamic title based on health - Pro look (Compact)
            pressure_label = get_status_label(stats.get('pressure_status', 'OK'))
            if stats.get('lag_risk'):
                self.title = f"STRESS! | CPU {stats['cpu']:.0f}% | MEM {stats['mem']:.0f}%"
            else:
                self.title = f"{pressure_label[:3]} | C:{stats['cpu']:.0f}% M:{stats['mem']:.0f}%"
            
            self._update_process_menu()
            
            # Check thresholds (using dynamic ones)
            alerts = self._check_dynamic_thresholds(stats)
            for title, message in alerts:
                notify(title, message)
                
        except Exception as e:
            self.title = "SYSTEM ERROR"
            logger.error(f"Error updating stats: {e}", exc_info=True)

    def _check_dynamic_thresholds(self, stats):
        """Check thresholds using the instance's limits."""
        # This is a bit redundant with core.check_thresholds but allows dynamic limits
        alerts = []
        if stats['cpu'] >= self.cpu_limit and can_notify('cpu'):
            alerts.append(("High CPU", f"CPU at {stats['cpu']:.1f}%"))
        if stats['mem'] >= self.mem_limit and can_notify('mem'):
            alerts.append(("High Memory", f"Memory at {stats['mem']:.1f}%"))
        if stats['swap'] >= self.swap_limit and can_notify('swap'):
            alerts.append(("High Swap", f"Swap at {stats['swap']:.1f}%"))
        
        # Add macOS specific ones from core
        if sys.platform == 'darwin':
            if stats.get('pressure_status') in ['WARN', 'HIGH'] and can_notify('pressure'):
                alerts.append(("Memory Pressure", f"Status: {stats['pressure_status']}"))
            if stats.get('lag_risk') and can_notify('lag_risk'):
                m = stats.get('macos_mem', {})
                alerts.append(("Lag Risk Detected", f"Compressed > Active"))
        return alerts
    
    def _refresh(self, _):
        """Manual refresh."""
        logger.info("Manual refresh triggered")
        self._update(None)
        notify("Monarx", "Refreshed")
    
    def _view_logs(self, _):
        """Open log file in default text editor."""
        from pathlib import Path
        log_file = Path.home() / "Library" / "Logs" / "Monarx" / "monarx.log"
        
        if log_file.exists():
            import subprocess
            subprocess.run(['open', '-t', str(log_file)])
            logger.info(f"Opened log file: {log_file}")
        else:
            notify("Monarx", "Log file not found yet")
            logger.warning("Log file not found")
    
    def _quit(self, _):
        """Quit application."""
        logger.info("Quitting Monarx")
        rumps.quit_application()


def run():
    """Run the macOS app."""
    # Setup logging first
    setup_logging(log_level=logging.INFO, log_to_file=True)
    logger.info("=" * 50)
    logger.info("Monarx starting up...")
    logger.info(f"Thresholds - CPU: {CPU_LIMIT}%, Memory: {MEM_LIMIT}%, Swap: {SWAP_LIMIT}%")
    logger.info(f"Check interval: {CHECK_EVERY} seconds")
    
    try:
        setup_macos()
        app = MonarxApp()
        logger.info("Monarx app running")
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Monarx shutting down...")
