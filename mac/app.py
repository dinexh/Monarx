"""Monarx - macOS menu bar implementation."""

import sys
import uuid
import logging
import subprocess
from pathlib import Path

import rumps

from core.config import (
    CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, CHECK_EVERY,
    __version__, load_thresholds, save_thresholds,
)
from core import get_stats, get_status, check_thresholds, get_combined_process_info, can_notify
from core.logging import setup_logging

logger = logging.getLogger('monarx.mac')

# Icon path — drop any PNG here and it will be picked up automatically.
_ICON_PATH = Path(__file__).parent / "assets" / "icon.png"

# ── Notification centre (UserNotifications framework) ────────────────────────

_un_center = None          # UNUserNotificationCenter instance, or False if unavailable
_un_authorized = False     # Whether the user granted permission


def _get_center():
    """Return a UNUserNotificationCenter, or None if the framework is missing."""
    global _un_center
    if _un_center is None:
        try:
            from UserNotifications import UNUserNotificationCenter
            _un_center = UNUserNotificationCenter.currentNotificationCenter()
        except Exception as e:
            logger.warning(f"UserNotifications framework unavailable: {e}")
            _un_center = False
    return _un_center if _un_center is not False else None


def request_notification_permission():
    """Ask the user for notification permission on first launch."""
    center = _get_center()
    if not center:
        return
    try:
        from UserNotifications import UNAuthorizationOptionAlert, UNAuthorizationOptionSound

        def handler(granted, error):
            global _un_authorized
            _un_authorized = bool(granted)
            if granted:
                logger.info("Notification permission granted")
            else:
                logger.warning("Notification permission denied — using osascript fallback")

        center.requestAuthorizationWithOptions_completionHandler_(
            UNAuthorizationOptionAlert | UNAuthorizationOptionSound,
            handler,
        )
    except Exception as e:
        logger.error(f"Failed to request notification permission: {e}")


def _notify_un(center, title, message, subtitle, identifier):
    """Deliver a notification via UserNotifications framework.

    Using a stable identifier (derived from the alert type) means macOS
    replaces the existing notification in-place rather than stacking new ones.
    Attaches icon.png as a thumbnail so the image appears in every banner.
    Supports Alert style — the user can set this in System Settings >
    Notifications once the app is bundled with a proper bundle ID.
    """
    try:
        from UserNotifications import (
            UNMutableNotificationContent,
            UNNotificationAttachment,
            UNNotificationRequest,
            UNNotificationSound,
        )
        import Foundation

        content = UNMutableNotificationContent.alloc().init()
        content.setTitle_(str(title))
        content.setBody_(str(message))
        if subtitle:
            content.setSubtitle_(str(subtitle))
        content.setSound_(UNNotificationSound.defaultSound())

        # Attach the app icon so it appears as a thumbnail in the banner.
        if _ICON_PATH.exists():
            icon_url = Foundation.NSURL.fileURLWithPath_(str(_ICON_PATH))
            attachment, err = UNNotificationAttachment.attachmentWithIdentifier_URL_options_error_(
                "monarx-icon", icon_url, None, None
            )
            if attachment and not err:
                content.setAttachments_([attachment])
            elif err:
                logger.debug(f"Notification attachment error: {err}")

        # Stable ID → same alert replaces itself instead of stacking
        req_id = identifier or ("monarx." + title.lower().replace(" ", "-"))
        request = UNNotificationRequest.requestWithIdentifier_content_trigger_(
            req_id, content, None
        )

        def completion(error):
            if error:
                logger.warning(f"UserNotifications delivery error: {error}")

        center.addNotificationRequest_withCompletionHandler_(request, completion)
        logger.info(f"Notification (UN): [{req_id}] {title} — {message}")

    except Exception as e:
        logger.error(f"UserNotifications delivery failed, using osascript: {e}")
        _notify_osascript(title, message, subtitle)


def _notify_osascript(title, message, subtitle=""):
    """Fallback notification via osascript (banner style only)."""
    def esc(text):
        return str(text).replace('\\', '\\\\').replace('"', '\\"')

    script = f'display notification "{esc(message)}" with title "{esc(title)}"'
    if subtitle:
        script += f' subtitle "{esc(subtitle)}"'
    script += ' sound name "default"'

    try:
        subprocess.run(
            ['osascript', '-e', script],
            check=True, capture_output=True, timeout=5,
        )
        logger.info(f"Notification (osascript): {title} — {message}")
    except subprocess.TimeoutExpired:
        logger.warning(f"Notification timed out: {title} — {message}")
    except subprocess.CalledProcessError as e:
        logger.error(f"osascript notification failed: {e}")


def notify(title, message, subtitle="", identifier=None):
    """Send a macOS notification.

    Uses UserNotifications framework when available (supports Alert style
    and notification grouping/replacement). Falls back to osascript.

    Args:
        title:      Notification title.
        message:    Body text.
        subtitle:   Optional subtitle shown below the title.
        identifier: Stable ID for this alert type — same ID replaces the
                    previous notification rather than adding a new one.
                    Defaults to a slug derived from the title.
    """
    center = _get_center()
    if center:
        _notify_un(center, title, message, subtitle, identifier)
    else:
        _notify_osascript(title, message, subtitle)


def setup_macos():
    """Setup macOS-specific behavior (no Dock icon)."""
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    logger.info("macOS activation policy set to accessory (no Dock icon)")


def get_status_label(status):
    """Get short text label for a status value."""
    return {"OK": "OK", "WARN": "WARN", "HIGH": "HIGH"}.get(status, "OK")


def get_progress_bar(percent, width=10):
    """Create a simple ASCII progress bar."""
    filled = int(percent / 100 * width)
    filled = max(0, min(width, filled))
    return "[" + "■" * filled + "□" * (width - filled) + "]"


def format_process_name(name, max_length=28):
    """Format process name with smart truncation."""
    if len(name) <= max_length:
        return name
    if '.' in name:
        parts = name.rsplit('.', 1)
        if len(parts) == 2:
            ext = parts[1]
            max_base = max_length - len(ext) - 1
            return f"{name[:max_base]}….{ext}"
    return name[:max_length - 1] + "…"


class MonarxApp(rumps.App):
    """Menu bar application for system monitoring."""

    def __init__(self):
        # No icon in the menu bar — text title only.
        super().__init__(
            name="Monarx",
            title="Loading...",
            quit_button=None,
        )
        self.top_cpu_processes = []
        self.top_mem_processes = []
        self.current_stats = {}
        self._menu_updating = False

        # Load persisted thresholds (falls back to defaults if none saved)
        self.cpu_limit, self.mem_limit, self.swap_limit = load_thresholds()

        self._build_menu()
        logger.info("Monarx app initialized")

    def _build_menu(self):
        """Build the initial placeholder menu."""
        self.menu = [
            rumps.MenuItem("SYSTEM MONITOR", callback=None),
            None,
            "Loading...",
            None,
            rumps.MenuItem("SETTINGS", callback=None),
            rumps.MenuItem("  Change Thresholds", callback=self._change_thresholds),
            None,
            rumps.MenuItem("REFRESH", callback=self._refresh),
            rumps.MenuItem("VIEW LOGS", callback=self._view_logs),
            rumps.MenuItem(f"Monarx v{__version__}", callback=None),
            None,
            rumps.MenuItem("QUIT", callback=self._quit),
        ]

    def _change_thresholds(self, _):
        """Change monitoring thresholds via a dialog."""
        response = rumps.Window(
            message=(
                f"Current: CPU={self.cpu_limit}%, Mem={self.mem_limit}%, Swap={self.swap_limit}%\n"
                f"Enter new values as 'CPU MEM SWAP' (e.g., '90 85 30').\n"
                f"Each value must be between 1 and 100."
            ),
            title="Update Thresholds",
            cancel=True,
        ).run()

        if response.clicked:
            try:
                vals = response.text.split()
                if len(vals) != 3:
                    rumps.alert("Please enter exactly three numbers separated by spaces (e.g., '90 85 30').")
                    return
                cpu, mem, swap = int(vals[0]), int(vals[1]), int(vals[2])
                if not all(1 <= v <= 100 for v in (cpu, mem, swap)):
                    rumps.alert("Each value must be between 1 and 100.")
                    return
                self.cpu_limit = cpu
                self.mem_limit = mem
                self.swap_limit = swap
                save_thresholds(cpu, mem, swap)
                notify("Monarx", f"Thresholds set: CPU {cpu}% | MEM {mem}% | SWAP {swap}%")
                logger.info(f"Thresholds updated: CPU={cpu}, Mem={mem}, Swap={swap}")
                self._update(None)
            except ValueError:
                rumps.alert("Invalid input. Please enter three whole numbers (e.g., '90 85 30').")
                logger.error("Error updating thresholds: invalid number format")
            except Exception as e:
                rumps.alert("Something went wrong. Please try again.")
                logger.error(f"Error updating thresholds: {e}")

    def _kill_process(self, sender):
        """Send SIGTERM to a process."""
        import os
        import signal
        pid = sender.pid
        name = sender.proc_name
        try:
            os.kill(pid, signal.SIGTERM)
            notify("Monarx", f"Sent SIGTERM to {name} (PID: {pid})")
            logger.info(f"Killed process {name} (PID: {pid})")
            self._update(None)
        except Exception as e:
            notify("Monarx", f"Failed to kill {name}: {e}")
            logger.error(f"Error killing process {pid}: {e}")

    def _open_process_info(self, sender):
        """Open Activity Monitor."""
        subprocess.run(['open', '-a', 'Activity Monitor'])

    def _update_process_menu(self):
        """Rebuild the full dropdown menu with current stats."""
        if self._menu_updating:
            return
        self._menu_updating = True

        try:
            stats = self.current_stats
            if not stats:
                return

            cpu_procs, mem_procs, gpu_procs = get_combined_process_info(limit=5)

            # ── Header ──────────────────────────────────────────────────
            pressure_label = get_status_label(stats.get('pressure_status', 'OK'))
            lag_state = "STRESSED" if stats.get('lag_risk') else "HEALTHY"
            summary_title = f"System Health: {pressure_label} Pressure | {lag_state}"

            # ── CPU ──────────────────────────────────────────────────────
            cpu_status = get_status_label(get_status(stats['cpu'], self.cpu_limit))
            cpu_line = f"CPU {get_progress_bar(stats['cpu'])} {stats['cpu']:.1f}%  [{cpu_status}]"

            # ── GPU heuristic ────────────────────────────────────────────
            gpu_activity = "IDLE"
            if gpu_procs:
                total_gpu_cpu = sum(p['cpu'] for p in gpu_procs)
                if total_gpu_cpu > 50:
                    gpu_activity = "HEAVY"
                elif total_gpu_cpu > 10:
                    gpu_activity = "MODERATE"

            # ── Memory breakdown ─────────────────────────────────────────
            m = stats.get('macos_mem') or {}
            total_gb = stats.get('mem_total_gb', 0)
            mem_breakdown = []
            if m:
                compressed = m.get('compressed', 0)
                active = m.get('active', 0)
                compressed_flag = "  (HIGH)" if compressed > active else ""
                mem_breakdown = [
                    rumps.MenuItem(
                        f"RAM {get_progress_bar(stats['mem'])} {stats['mem']:.1f}%"
                        + (f" of {total_gb:.1f} GB" if total_gb else "")
                    ),
                    rumps.MenuItem(f"  Wired:      {m.get('wired', 0):.2f} GB"),
                    rumps.MenuItem(f"  Active:     {active:.2f} GB"),
                    rumps.MenuItem(f"  Compressed: {compressed:.2f} GB{compressed_flag}"),
                    rumps.MenuItem(f"  Cached:     {m.get('cached', 0):.2f} GB"),
                ]

            swap_line = f"Swap {get_progress_bar(stats['swap'])} {stats['swap']:.1f}%"

            # ── Assemble ─────────────────────────────────────────────────
            menu_items = [
                rumps.MenuItem(summary_title),
                None,
                rumps.MenuItem(cpu_line),
                rumps.MenuItem(f"GPU Activity: {gpu_activity}"),
                None,
            ]

            menu_items.extend(mem_breakdown)
            menu_items.append(rumps.MenuItem(swap_line))
            menu_items.append(None)

            # Thresholds
            menu_items.extend([
                rumps.MenuItem("SETTINGS"),
                rumps.MenuItem(
                    f"  Thresholds: CPU {self.cpu_limit}% | MEM {self.mem_limit}% | SWAP {self.swap_limit}%",
                    callback=self._change_thresholds,
                ),
                None,
            ])

            # Top CPU processes
            menu_items.append(rumps.MenuItem("TOP CPU PROCESSES:"))
            for p in cpu_procs:
                p_item = rumps.MenuItem(f"  {format_process_name(p['name'], 25)}: {p['cpu']:.1f}%")
                kill_item = rumps.MenuItem("Kill Process", callback=self._kill_process)
                kill_item.pid = p['pid']
                kill_item.proc_name = p['raw_name']
                info_item = rumps.MenuItem("Open Activity Monitor", callback=self._open_process_info)
                info_item.pid = p['pid']
                p_item.add(kill_item)
                p_item.add(info_item)
                menu_items.append(p_item)

            menu_items.append(None)

            # Top memory processes
            menu_items.append(rumps.MenuItem("TOP MEMORY PROCESSES:"))
            for p in mem_procs:
                p_item = rumps.MenuItem(f"  {format_process_name(p['name'], 25)}: {p['mem']:.1f}%")
                kill_item = rumps.MenuItem("Kill Process", callback=self._kill_process)
                kill_item.pid = p['pid']
                kill_item.proc_name = p['raw_name']
                p_item.add(kill_item)
                menu_items.append(p_item)

            # Footer actions
            menu_items.extend([
                None,
                rumps.MenuItem("REFRESH", callback=self._refresh),
                rumps.MenuItem("VIEW LOGS", callback=self._view_logs),
                rumps.MenuItem(f"Monarx v{__version__}", callback=None),
                None,
                rumps.MenuItem("QUIT", callback=self._quit),
            ])

            # Replace menu atomically
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
        """Fetch stats and refresh title + menu on every timer tick."""
        try:
            stats = get_stats()
            self.current_stats = stats

            # Menu bar title — compact and contextual
            pressure = stats.get('pressure_status', 'OK')
            cpu_s = f"C:{stats['cpu']:.0f}%"
            mem_s = f"M:{stats['mem']:.0f}%"

            if stats.get('lag_risk'):
                self.title = f"STRESS {cpu_s} {mem_s}"
            elif pressure == 'HIGH':
                self.title = f"HIGH {cpu_s} {mem_s}"
            elif pressure == 'WARN':
                self.title = f"WARN {cpu_s} {mem_s}"
            else:
                self.title = f"{cpu_s} {mem_s}"

            self._update_process_menu()

            alerts = check_thresholds(
                stats,
                cpu_limit=self.cpu_limit,
                mem_limit=self.mem_limit,
                swap_limit=self.swap_limit,
            )
            for title, message in alerts:
                notify(title, message)

        except Exception as e:
            self.title = "ERROR"
            logger.error(f"Error updating stats: {e}", exc_info=True)

    def _refresh(self, _):
        """Manual refresh."""
        logger.info("Manual refresh triggered")
        self._update(None)
        notify("Monarx", "Refreshed")

    def _view_logs(self, _):
        """Open log file in the default text editor."""
        log_file = Path.home() / "Library" / "Logs" / "Monarx" / "monarx.log"
        if log_file.exists():
            import subprocess
            subprocess.run(['open', '-t', str(log_file)])
            logger.info(f"Opened log file: {log_file}")
        else:
            notify("Monarx", "Log file not found yet")
            logger.warning("Log file not found")

    def _quit(self, _):
        """Quit the application."""
        logger.info("Quitting Monarx")
        rumps.quit_application()


def run():
    """Run the macOS app."""
    setup_logging(log_level=logging.INFO, log_to_file=True)
    logger.info("=" * 50)
    logger.info(f"Monarx v{__version__} starting up...")
    logger.info(f"Thresholds - CPU: {CPU_LIMIT}%, Memory: {MEM_LIMIT}%, Swap: {SWAP_LIMIT}%")
    logger.info(f"Check interval: {CHECK_EVERY} seconds")

    try:
        setup_macos()
        request_notification_permission()
        app = MonarxApp()
        logger.info("Monarx app running")
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Monarx shutting down...")
