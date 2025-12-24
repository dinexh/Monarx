import sys
import os

# Check platform first
if sys.platform != "darwin":
    print("Error: Mac Monitor only runs on macOS")
    sys.exit(1)

import bootstrap
import rumps
import psutil
import time

from config import CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, CHECK_EVERY, COOLDOWN



# SYSTEM STATS

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



# NOTIFICATIONS


_last_alert = {}

def notify(title, message):
    """Send a macOS notification."""
    # Use rumps.notification to avoid shell-based command execution
    rumps.notification(title, "", message)


def can_notify(key):
    """Check if notification can be sent (respects cooldown)."""
    now = time.time()
    if key not in _last_alert or now - _last_alert[key] > COOLDOWN:
        _last_alert[key] = now
        return True
    return False


def check_and_notify(stats):
    """Send notifications if thresholds exceeded."""
    if stats['cpu'] >= CPU_LIMIT and can_notify('cpu'):
        notify("High CPU", f"CPU at {stats['cpu']:.1f}%")
    if stats['mem'] >= MEM_LIMIT and can_notify('mem'):
        notify("High Memory", f"Memory at {stats['mem']:.1f}%")
    if stats['swap'] >= SWAP_LIMIT and can_notify('swap'):
        notify("High Swap", f"Swap at {stats['swap']:.1f}%")


# MENU BAR APP


class MacMonitorApp(rumps.App):
    """Menu bar application for system monitoring."""
    
    def __init__(self):
        super().__init__(name="Mac Monitor", title="Loading...", quit_button=None)
        self._build_menu()
    
    def _build_menu(self):
        """Build the dropdown menu."""
        # Stats items
        self.cpu_item = rumps.MenuItem("CPU: --%")
        self.mem_item = rumps.MenuItem("Memory: --%")
        self.swap_item = rumps.MenuItem("Swap: --%")
        
        # Threshold items
        self.menu = [
            self.cpu_item,
            self.mem_item,
            self.swap_item,
            None,
            rumps.MenuItem("Thresholds:"),
            rumps.MenuItem(f"  CPU: {CPU_LIMIT}%"),
            rumps.MenuItem(f"  Memory: {MEM_LIMIT}%"),
            rumps.MenuItem(f"  Swap: {SWAP_LIMIT}%"),
            None,
            rumps.MenuItem("Refresh", callback=self._refresh),
            rumps.MenuItem("Quit", callback=self._quit)
        ]
    
    @rumps.timer(CHECK_EVERY)
    def _update(self, _):
        """Update stats on timer."""
        try:
            stats = get_stats()
            
            # Update title
            self.title = f"C:{stats['cpu']:.0f} M:{stats['mem']:.0f} S:{stats['swap']:.0f}"
            
            # Update menu items
            self.cpu_item.title = f"CPU: {stats['cpu']:.1f}% [{get_status(stats['cpu'], CPU_LIMIT)}]"
            self.mem_item.title = f"Memory: {stats['mem']:.1f}% [{get_status(stats['mem'], MEM_LIMIT)}]"
            self.swap_item.title = f"Swap: {stats['swap']:.1f}% [{get_status(stats['swap'], SWAP_LIMIT)}]"
            
            # Check thresholds
            check_and_notify(stats)
            
        except Exception as e:
            self.title = "Error"
            print(f"Error: {e}", file=sys.stderr)
    
    def _refresh(self, _):
        """Manual refresh."""
        self._update(None)
        rumps.notification("Mac Monitor", "", "Refreshed")
    
    def _quit(self, _):
        """Quit application."""
        rumps.quit_application()


if __name__ == "__main__":
    MacMonitorApp().run()
