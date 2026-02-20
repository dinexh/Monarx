"""MacMonitor - macOS menu bar implementation."""

import sys
import uuid
import logging
import subprocess
from pathlib import Path

import time
import rumps

from core.config import (
    CPU_LIMIT, MEM_LIMIT, SWAP_LIMIT, CHECK_EVERY,
    __version__, load_thresholds, save_thresholds,
)
from core import get_stats, get_status, check_thresholds, get_combined_process_info, can_notify
from core.logging import setup_logging

logger = logging.getLogger('macmonitor.mac')

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
                "macmonitor-icon", icon_url, None, None
            )
            if attachment and not err:
                content.setAttachments_([attachment])
            elif err:
                logger.debug(f"Notification attachment error: {err}")

        # Stable ID → same alert replaces itself instead of stacking
        req_id = identifier or ("macmonitor." + title.lower().replace(" ", "-"))
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


def get_mini_bar(value_gb: float, total_gb: float, width: int = 5) -> str:
    """Create a compact 5-char bar showing value as a fraction of total RAM."""
    if total_gb <= 0:
        return "[" + "□" * width + "]"
    filled = max(0, min(width, int((value_gb / total_gb) * width)))
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


class MacMonitorApp(rumps.App):
    """Menu bar application for system monitoring."""

    def __init__(self):
        # No icon in the menu bar — text title only.
        super().__init__(
            name="MacMonitor",
            title="Loading...",
            quit_button=None,
        )
        self.top_cpu_processes = []
        self.top_mem_processes = []
        self.current_stats = {}
        self._menu_updating = False
        self._last_updated: float | None = None

        # Load persisted thresholds (falls back to defaults if none saved)
        self.cpu_limit, self.mem_limit, self.swap_limit = load_thresholds()

        self._build_menu()
        logger.info("MacMonitor app initialized")

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
            rumps.MenuItem(f"MacMonitor v{__version__}", callback=None),
            None,
            rumps.MenuItem("QUIT", callback=self._quit),
        ]

    # ── Colour palette ────────────────────────────────────────────────────
    # Defined as a method so NSColor is only imported after the app is running.
    #
    #   green  #4DCC80  – OK
    #   blue   #5B9CF6  – WARN
    #   red    #EB5252  – HIGH / STRESS
    #
    @staticmethod
    def _palette():
        from AppKit import NSColor
        def srgb(r, g, b, a=1.0):
            return NSColor.colorWithSRGBRed_green_blue_alpha_(r, g, b, a)
        return {
            'emerald': srgb(0.30, 0.80, 0.50),        # OK    – green
            'blue':    srgb(0.36, 0.61, 0.96),        # WARN  – blue
            'coral':   srgb(0.92, 0.32, 0.32),        # HIGH  – red
            # softer variants for the health header row
            'blue_soft':  srgb(0.36, 0.61, 0.96, 0.88),
            'coral_soft': srgb(0.92, 0.32, 0.32, 0.88),
            # text hierarchy
            'primary':   NSColor.labelColor(),
            'secondary': NSColor.secondaryLabelColor(),
            'tertiary':  NSColor.tertiaryLabelColor(),
        }

    def _colored_bar_item(self, text, status):
        """Return a MenuItem where filled bar chars (■) are colored by status."""
        item = rumps.MenuItem(text)
        try:
            from AppKit import NSMutableAttributedString, NSForegroundColorAttributeName
            p = self._palette()
            color = {'OK': p['emerald'], 'WARN': p['blue'], 'HIGH': p['coral']}.get(
                status, p['primary']
            )
            attr_str = NSMutableAttributedString.alloc().initWithString_(text)
            start = 0
            while True:
                idx = text.find('■', start)
                if idx == -1:
                    break
                attr_str.addAttribute_value_range_(
                    NSForegroundColorAttributeName, color, (idx, 1)
                )
                start = idx + 1
            item._menuitem.setAttributedTitle_(attr_str)
        except Exception as e:
            logger.debug(f"Colored bar item unavailable: {e}")
        return item

    def _styled_item(self, text, style='primary', callback=None):
        """Create a MenuItem with a colour from the shared palette.

        Styles
        ------
        primary      full-brightness label colour (default menu text)
        secondary    dim gray  — sub-rows, GPU line, thresholds
        tertiary     dimmer    — section labels, footer timestamp
        health_ok    secondary gray (system healthy)
        health_warn  soft amber (warning pressure)
        health_high  soft coral (high pressure / stress)
        """
        item = rumps.MenuItem(text, callback=callback)
        try:
            from AppKit import NSMutableAttributedString, NSForegroundColorAttributeName
            p = self._palette()
            color = {
                'primary':     p['primary'],
                'secondary':   p['secondary'],
                'tertiary':    p['tertiary'],
                'health_ok':   p['secondary'],
                'health_warn': p['blue_soft'],
                'health_high': p['coral_soft'],
            }.get(style, p['primary'])
            attr_str = NSMutableAttributedString.alloc().initWithString_(text)
            attr_str.addAttribute_value_range_(
                NSForegroundColorAttributeName, color, (0, len(text))
            )
            item._menuitem.setAttributedTitle_(attr_str)
        except Exception as e:
            logger.debug(f"Styled item unavailable: {e}")
        return item

    def _change_thresholds(self, _):
        """Change monitoring thresholds via individual per-metric prompts."""
        def ask(title, message, current):
            resp = rumps.Window(
                message=message,
                title=title,
                default_text=str(current),
                cancel=True,
            ).run()
            if not resp.clicked:
                return None
            try:
                val = int(resp.text.strip())
                if not 1 <= val <= 100:
                    rumps.alert(f"{title}: value must be between 1 and 100.")
                    return None
                return val
            except ValueError:
                rumps.alert(f"{title}: enter a whole number between 1 and 100.")
                return None

        cpu = ask("CPU Threshold", f"Alert when CPU exceeds this % (current: {self.cpu_limit}%)", self.cpu_limit)
        if cpu is None:
            return
        mem = ask("Memory Threshold", f"Alert when RAM exceeds this % (current: {self.mem_limit}%)", self.mem_limit)
        if mem is None:
            return
        swap = ask("Swap Threshold", f"Alert when Swap exceeds this % (current: {self.swap_limit}%)", self.swap_limit)
        if swap is None:
            return

        self.cpu_limit = cpu
        self.mem_limit = mem
        self.swap_limit = swap
        save_thresholds(cpu, mem, swap)
        notify("MacMonitor", f"Thresholds updated: CPU {cpu}% | MEM {mem}% | SWAP {swap}%")
        logger.info(f"Thresholds updated: CPU={cpu}, Mem={mem}, Swap={swap}")
        self._update(None)

    def _kill_process(self, sender):
        """Send SIGTERM to a process."""
        import os
        import signal
        pid = sender.pid
        name = sender.proc_name
        try:
            os.kill(pid, signal.SIGTERM)
            notify("MacMonitor", f"Sent SIGTERM to {name} (PID: {pid})")
            logger.info(f"Killed process {name} (PID: {pid})")
            self._update(None)
        except Exception as e:
            notify("MacMonitor", f"Failed to kill {name}: {e}")
            logger.error(f"Error killing process {pid}: {e}")

    def _open_process_info(self, sender):
        """Open Activity Monitor."""
        subprocess.run(['open', '-a', 'Activity Monitor'])

    def _copy_stats(self, _):
        """Copy the current stats snapshot to the clipboard via pbcopy."""
        if not self.current_stats:
            notify("MacMonitor", "No stats available yet — try again in a moment.")
            return
        stats = self.current_stats
        m = stats.get('macos_mem') or {}
        lines = [
            f"MacMonitor Snapshot — {time.strftime('%H:%M:%S')}",
            f"CPU: {stats['cpu']:.1f}%  RAM: {stats['mem']:.1f}%  Swap: {stats['swap']:.1f}%",
            f"Pressure: {stats.get('pressure_status', 'N/A')}  Lag Risk: {'Yes' if stats.get('lag_risk') else 'No'}",
        ]
        if m:
            lines.append(
                f"Wired: {m.get('wired', 0):.2f} GB  "
                f"Active: {m.get('active', 0):.2f} GB  "
                f"Compressed: {m.get('compressed', 0):.2f} GB  "
                f"Cached: {m.get('cached', 0):.2f} GB"
            )
        try:
            subprocess.run(['pbcopy'], input="\n".join(lines).encode(), check=True, timeout=3)
            notify("MacMonitor", "Stats copied to clipboard")
            logger.info("Stats copied to clipboard")
        except Exception as e:
            logger.error(f"Failed to copy stats: {e}")

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

            # ── Status values ─────────────────────────────────────────────
            cpu_status  = get_status(stats['cpu'],  self.cpu_limit)
            mem_status  = get_status(stats['mem'],  self.mem_limit)
            swap_status = get_status(stats['swap'], self.swap_limit)

            # ── Health header (short, status-colored) ────────────────────
            pressure_label = get_status_label(stats.get('pressure_status', 'OK'))
            lag_risk = stats.get('lag_risk', False)
            lag_state = "STRESSED" if lag_risk else "HEALTHY"
            summary_title = f"{pressure_label} · {lag_state}"

            if lag_risk or pressure == 'HIGH':
                health_style = 'health_high'
            elif pressure == 'WARN':
                health_style = 'health_warn'
            else:
                health_style = 'health_ok'

            # ── CPU ──────────────────────────────────────────────────────
            cpu_item = self._colored_bar_item(
                f"CPU  {get_progress_bar(stats['cpu'])}  {stats['cpu']:.1f}%",
                cpu_status,
            )

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
                active     = m.get('active', 0)
                wired      = m.get('wired', 0)
                cached     = m.get('cached', 0)
                compressed_flag = "  ← HIGH" if compressed > active else ""

                ram_text = f"RAM  {get_progress_bar(stats['mem'])}  {stats['mem']:.1f}%"
                if total_gb:
                    ram_text += f"  {total_gb:.1f} GB"
                ram_item = self._colored_bar_item(ram_text, mem_status)

                mem_breakdown = [
                    ram_item,
                    self._styled_item(f"  Wired       {wired:.2f} GB", 'secondary'),
                    self._styled_item(f"  Active      {active:.2f} GB", 'secondary'),
                    self._styled_item(f"  Compressed  {compressed:.2f} GB{compressed_flag}", 'secondary'),
                    self._styled_item(f"  Cached      {cached:.2f} GB", 'secondary'),
                ]

            swap_item = self._colored_bar_item(
                f"SWAP  {get_progress_bar(stats['swap'])}  {stats['swap']:.1f}%",
                swap_status,
            )

            # ── Process submenu ───────────────────────────────────────────
            proc_menu = rumps.MenuItem("Processes")

            proc_menu.add(self._styled_item("CPU", 'tertiary'))
            for p in cpu_procs:
                p_item = rumps.MenuItem(f"  {format_process_name(p['name'], 24)}  {p['cpu']:.1f}%")
                kill_item = rumps.MenuItem("Kill Process", callback=self._kill_process)
                kill_item.pid = p['pid']
                kill_item.proc_name = p['raw_name']
                info_item = rumps.MenuItem("Open Activity Monitor", callback=self._open_process_info)
                info_item.pid = p['pid']
                p_item.add(kill_item)
                p_item.add(info_item)
                proc_menu.add(p_item)

            proc_menu.add(self._styled_item("Memory", 'tertiary'))
            for p in mem_procs:
                p_item = rumps.MenuItem(f"  {format_process_name(p['name'], 24)}  {p['mem']:.1f}%")
                kill_item = rumps.MenuItem("Kill Process", callback=self._kill_process)
                kill_item.pid = p['pid']
                kill_item.proc_name = p['raw_name']
                p_item.add(kill_item)
                proc_menu.add(p_item)

            # ── Footer timestamp ──────────────────────────────────────────
            updated_str = (
                time.strftime('%H:%M:%S', time.localtime(self._last_updated))
                if self._last_updated else "--:--:--"
            )

            # ── Assemble ─────────────────────────────────────────────────
            menu_items = [
                self._styled_item(summary_title, health_style),
                None,
                cpu_item,
                self._styled_item(f"  GPU · {gpu_activity}", 'secondary'),
                None,
            ]

            menu_items.extend(mem_breakdown)
            menu_items.append(swap_item)
            menu_items.append(None)

            menu_items.extend([
                self._styled_item(
                    f"  CPU {self.cpu_limit}% · MEM {self.mem_limit}% · SWAP {self.swap_limit}%",
                    'secondary',
                    callback=self._change_thresholds,
                ),
                None,
                rumps.MenuItem("Refresh", callback=self._refresh),
                rumps.MenuItem("View Logs", callback=self._view_logs),
                rumps.MenuItem("Copy Stats", callback=self._copy_stats),
                None,
                proc_menu,
                None,
                self._styled_item(f"v{__version__}  ·  {updated_str}", 'tertiary'),
                None,
                rumps.MenuItem("Quit", callback=self._quit),
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
            self._last_updated = time.time()

            # Menu bar title — compact, uses · as separator
            pressure = stats.get('pressure_status', 'OK')
            base = f"C:{stats['cpu']:.0f}% · M:{stats['mem']:.0f}%"

            if stats.get('lag_risk'):
                self.title = f"STRESS  {base}"
            elif pressure == 'HIGH':
                self.title = f"HIGH  {base}"
            elif pressure == 'WARN':
                self.title = f"WARN  {base}"
            else:
                self.title = base

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
        notify("MacMonitor", "Refreshed")

    def _view_logs(self, _):
        """Open log file in the default text editor."""
        log_file = Path.home() / "Library" / "Logs" / "MacMonitor" / "macmonitor.log"
        if log_file.exists():
            import subprocess
            subprocess.run(['open', '-t', str(log_file)])
            logger.info(f"Opened log file: {log_file}")
        else:
            notify("MacMonitor", "Log file not found yet")
            logger.warning("Log file not found")

    def _quit(self, _):
        """Quit the application."""
        logger.info("Quitting MacMonitor")
        rumps.quit_application()


def run():
    """Run the macOS app."""
    setup_logging(log_level=logging.INFO, log_to_file=True)
    logger.info("=" * 50)
    logger.info(f"MacMonitor v{__version__} starting up...")
    logger.info(f"Thresholds - CPU: {CPU_LIMIT}%, Memory: {MEM_LIMIT}%, Swap: {SWAP_LIMIT}%")
    logger.info(f"Check interval: {CHECK_EVERY} seconds")

    try:
        setup_macos()
        request_notification_permission()
        app = MacMonitorApp()
        logger.info("MacMonitor app running")
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        logger.info("MacMonitor shutting down...")
