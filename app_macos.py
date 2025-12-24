"""Monarx - macOS menu bar implementation."""

import sys
import rumps

from config import CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, CHECK_EVERY
from core import get_stats, get_status, check_thresholds


def setup_macos():
    """Setup macOS-specific behavior."""
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)


def notify(title, message):
    """Send a macOS notification."""
    rumps.notification(title, "", message)


class MonarxApp(rumps.App):
    """Menu bar application for system monitoring."""
    
    def __init__(self):
        super().__init__(name="Monarx", title="Loading...", quit_button=None)
        self._build_menu()
    
    def _build_menu(self):
        """Build the dropdown menu."""
        self.cpu_item = rumps.MenuItem("CPU: --%")
        self.mem_item = rumps.MenuItem("Memory: --%")
        self.swap_item = rumps.MenuItem("Swap: --%")
        
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
            
            self.title = f"C:{stats['cpu']:.0f} M:{stats['mem']:.0f} S:{stats['swap']:.0f}"
            
            self.cpu_item.title = f"CPU: {stats['cpu']:.1f}% [{get_status(stats['cpu'], CPU_LIMIT)}]"
            self.mem_item.title = f"Memory: {stats['mem']:.1f}% [{get_status(stats['mem'], MEM_LIMIT)}]"
            self.swap_item.title = f"Swap: {stats['swap']:.1f}% [{get_status(stats['swap'], SWAP_LIMIT)}]"
            
            for title, message in check_thresholds(stats):
                notify(title, message)
                
        except Exception as e:
            self.title = "Error"
            print(f"Error: {e}", file=sys.stderr)
    
    def _refresh(self, _):
        """Manual refresh."""
        self._update(None)
        notify("Monarx", "Refreshed")
    
    def _quit(self, _):
        """Quit application."""
        rumps.quit_application()


def run():
    """Run the macOS app."""
    setup_macos()
    MonarxApp().run()
