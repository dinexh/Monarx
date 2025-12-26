"""Monarx - macOS menu bar implementation."""

import sys
import logging
import rumps

from core.config import CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, CHECK_EVERY
from core import get_stats, get_status, check_thresholds, get_top_processes
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


def get_status_icon(status):
    """Get emoji icon for status."""
    icons = {
        "OK": "✓",
        "WARN": "⚠️",
        "HIGH": "🔴"
    }
    return icons.get(status, "•")


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
        self.current_stats = {'cpu': 0, 'mem': 0, 'swap': 0}
        self._menu_updating = False
        self._build_menu()
        logger.info("Monarx app initialized")
    
    def _build_menu(self):
        """Build the dropdown menu."""
        self.cpu_item = rumps.MenuItem("💻 CPU: --%")
        self.mem_item = rumps.MenuItem("🧠 Memory: --%")
        self.swap_item = rumps.MenuItem("💾 Swap: --%")
        
        # Top processes section - will be updated dynamically
        self.top_cpu_processes = []
        self.top_mem_processes = []
        self.top_cpu_items = []
        self.top_mem_items = []
        
        # Build initial menu with improved UI
        menu_items = [
            rumps.MenuItem("📊 System Status", callback=None),
            None,
            self.cpu_item,
            self.mem_item,
            self.swap_item,
            None,
            rumps.MenuItem("⚙️ Thresholds", callback=None),
            rumps.MenuItem(f"  CPU: {CPU_LIMIT}%"),
            rumps.MenuItem(f"  Memory: {MEM_LIMIT}%"),
            rumps.MenuItem(f"  Swap: {SWAP_LIMIT}%"),
            None,
            rumps.MenuItem("🔥 Top CPU Processes"),
            rumps.MenuItem("  ⏳ Loading...", callback=None),
            None,
            rumps.MenuItem("💾 Top Memory Processes"),
            rumps.MenuItem("  ⏳ Loading...", callback=None),
            None,
            rumps.MenuItem("🔄 Refresh", callback=self._refresh),
            rumps.MenuItem("📝 View Logs", callback=self._view_logs),
            None,
            rumps.MenuItem("❌ Quit", callback=self._quit)
        ]
        
        self.menu = menu_items
        # Store indices for process sections
        self.cpu_start_idx = 12  # Index of "Top CPU Processes" + 1
        self.mem_start_idx = 15  # Index of "Top Memory Processes" + 1
    
    def _update_process_menu(self):
        """Update the top processes menu items."""
        # Prevent concurrent menu updates
        if self._menu_updating:
            return
        self._menu_updating = True
        
        try:
            # Get top processes
            self.top_cpu_processes = get_top_processes(by='cpu', limit=5)
            self.top_mem_processes = get_top_processes(by='memory', limit=5)
            
            # Get current stats for menu items
            stats = self.current_stats
            cpu_title = f"CPU: {stats['cpu']:.1f}% [{get_status(stats['cpu'], CPU_LIMIT)}]"
            mem_title = f"Memory: {stats['mem']:.1f}% [{get_status(stats['mem'], MEM_LIMIT)}]"
            swap_title = f"Swap: {stats['swap']:.1f}% [{get_status(stats['swap'], SWAP_LIMIT)}]"
            
            # Rebuild menu by creating ALL new menu items to avoid reuse issues
            self.cpu_item = rumps.MenuItem(cpu_title)
            self.mem_item = rumps.MenuItem(mem_title)
            self.swap_item = rumps.MenuItem(swap_title)
            
            menu_items = [
                self.cpu_item,
                self.mem_item,
                self.swap_item,
                None,
                rumps.MenuItem("Thresholds:"),
                rumps.MenuItem(f"  CPU: {CPU_LIMIT}%"),
                rumps.MenuItem(f"  Memory: {MEM_LIMIT}%"),
                rumps.MenuItem(f"  Swap: {SWAP_LIMIT}%"),
                None,
                rumps.MenuItem("Top CPU Processes:"),
            ]
            
            # Add CPU processes
            if self.top_cpu_processes:
                for name, pid, usage in self.top_cpu_processes:
                    display_name = name[:30] if len(name) > 30 else name
                    menu_items.append(
                        rumps.MenuItem(f"  {display_name}: {usage:.1f}% (PID: {pid})", callback=None)
                    )
            else:
                menu_items.append(rumps.MenuItem("  No processes found", callback=None))
            
            menu_items.append(None)
            menu_items.append(rumps.MenuItem("Top Memory Processes:"))
            
            # Add Memory processes
            if self.top_mem_processes:
                for name, pid, usage in self.top_mem_processes:
                    display_name = name[:30] if len(name) > 30 else name
                    menu_items.append(
                        rumps.MenuItem(f"  {display_name}: {usage:.1f}% (PID: {pid})", callback=None)
                    )
            else:
                menu_items.append(rumps.MenuItem("  No processes found", callback=None))
            
            menu_items.extend([
                None,
                rumps.MenuItem("Refresh", callback=self._refresh),
                rumps.MenuItem("View Logs", callback=self._view_logs),
                rumps.MenuItem("Quit", callback=self._quit)
            ])
            
            # IMPORTANT: Clear the menu first by removing all items
            # This prevents rumps from appending instead of replacing
            try:
                if hasattr(self, '_menu') and self._menu:
                    # Access the internal NSMenu object and clear it
                    ns_menu = self._menu._menu
                    if ns_menu:
                        ns_menu.removeAllItems()
            except Exception as e:
                logger.debug(f"Error clearing menu: {e}")
            
            # Now set the new menu - this should replace, not append
            # Setting menu to list should replace, but we cleared first to be sure
            self.menu = menu_items
        finally:
            self._menu_updating = False
    
    @rumps.timer(CHECK_EVERY)
    def _update(self, _):
        """Update stats on timer."""
        try:
            stats = get_stats()
            
            self.title = f"C:{stats['cpu']:.0f} M:{stats['mem']:.0f} S:{stats['swap']:.0f}"
            
            # Store current stats for menu rebuild
            self.current_stats = stats
            
            # Update top processes menu (which will rebuild menu with updated stats)
            self._update_process_menu()
            
            # Check thresholds and send notifications
            alerts = check_thresholds(stats)
            for title, message in alerts:
                notify(title, message)
            
            logger.debug(
                f"Stats updated - CPU: {stats['cpu']:.1f}%, "
                f"Memory: {stats['mem']:.1f}%, Swap: {stats['swap']:.1f}%"
            )
                
        except Exception as e:
            self.title = "Error"
            logger.error(f"Error updating stats: {e}", exc_info=True)
            print(f"Error: {e}", file=sys.stderr)
    
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
