"""Unit and integration tests for Monarx core logic."""

import json
import sys
import time
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch


# ── Pure function tests (no macOS deps) ──────────────────────────────────────

class TestGetStatus:
    def test_ok_below_warn(self):
        from core import get_status
        assert get_status(50, 85) == "OK"

    def test_warn_at_threshold(self):
        from core import get_status
        # warn_factor=0.85 → warn starts at 85*0.85 = 72.25
        assert get_status(73, 85) == "WARN"

    def test_high_at_limit(self):
        from core import get_status
        assert get_status(85, 85) == "HIGH"

    def test_high_above_limit(self):
        from core import get_status
        assert get_status(99, 85) == "HIGH"

    def test_zero_value_is_ok(self):
        from core import get_status
        assert get_status(0, 85) == "OK"

    def test_custom_warn_factor(self):
        from core import get_status
        # warn_factor=0.5 → warn starts at 50
        assert get_status(50, 100, warn_factor=0.5) == "WARN"


class TestGetProgressBar:
    def test_empty_bar(self):
        from mac.app import get_progress_bar
        assert get_progress_bar(0) == "[□□□□□□□□□□]"

    def test_full_bar(self):
        from mac.app import get_progress_bar
        assert get_progress_bar(100) == "[■■■■■■■■■■]"

    def test_half_bar(self):
        from mac.app import get_progress_bar
        bar = get_progress_bar(50)
        assert bar.count("■") == 5
        assert bar.count("□") == 5

    def test_bar_total_width(self):
        from mac.app import get_progress_bar
        bar = get_progress_bar(37)
        # length = 2 brackets + 10 chars
        assert len(bar) == 12

    def test_over_100_clamps(self):
        from mac.app import get_progress_bar
        # should not raise or produce extra chars
        bar = get_progress_bar(110)
        assert bar == "[■■■■■■■■■■]"


class TestFormatProcessName:
    def test_short_name_unchanged(self):
        from mac.app import format_process_name
        assert format_process_name("python") == "python"

    def test_long_name_truncated(self):
        from mac.app import format_process_name
        name = "a" * 40
        result = format_process_name(name, max_length=28)
        assert len(result) <= 28

    def test_extension_preserved(self):
        from mac.app import format_process_name
        name = "a" * 30 + ".app"
        result = format_process_name(name, max_length=28)
        assert result.endswith(".app")

    def test_exact_length_unchanged(self):
        from mac.app import format_process_name
        name = "x" * 28
        assert format_process_name(name, max_length=28) == name


class TestGetStatusLabel:
    def test_ok(self):
        from mac.app import get_status_label
        assert get_status_label("OK") == "OK"

    def test_warn(self):
        from mac.app import get_status_label
        assert get_status_label("WARN") == "WARN"

    def test_high(self):
        from mac.app import get_status_label
        assert get_status_label("HIGH") == "HIGH"

    def test_unknown_defaults_to_ok(self):
        from mac.app import get_status_label
        assert get_status_label("UNKNOWN") == "OK"


# ── Notification cooldown tests ───────────────────────────────────────────────

class TestCanNotify:
    def setup_method(self):
        # Reset cooldown state before each test
        import core as core_module
        core_module._last_alert = {}

    def test_first_call_allowed(self):
        from core import can_notify
        assert can_notify("test_key") is True

    def test_immediate_second_call_blocked(self):
        from core import can_notify
        can_notify("cpu")
        assert can_notify("cpu") is False

    def test_different_keys_independent(self):
        from core import can_notify
        can_notify("cpu")
        assert can_notify("mem") is True

    def test_allowed_after_cooldown(self):
        from core import can_notify
        import core as core_module
        can_notify("cpu")
        # Backdate the last alert to simulate cooldown expiry
        core_module._last_alert["cpu"] = time.time() - 200
        assert can_notify("cpu") is True


# ── Threshold persistence tests ───────────────────────────────────────────────

class TestThresholdPersistence:
    def test_save_and_load(self, tmp_path):
        from core import config as cfg
        config_file = tmp_path / "config.json"
        with patch.object(cfg, '_config_file', return_value=config_file):
            cfg.save_thresholds(90, 75, 30)
            cpu, mem, swap = cfg.load_thresholds()
        assert cpu == 90
        assert mem == 75
        assert swap == 30

    def test_load_returns_defaults_when_missing(self, tmp_path):
        from core import config as cfg
        missing_file = tmp_path / "nonexistent.json"
        with patch.object(cfg, '_config_file', return_value=missing_file):
            cpu, mem, swap = cfg.load_thresholds()
        assert cpu == cfg.CPU_LIMIT
        assert mem == cfg.MEM_LIMIT
        assert swap == cfg.SWAP_LIMIT

    def test_load_clamps_out_of_range(self, tmp_path):
        from core import config as cfg
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({'cpu_limit': 200, 'mem_limit': -5, 'swap_limit': 50}))
        with patch.object(cfg, '_config_file', return_value=config_file):
            cpu, mem, swap = cfg.load_thresholds()
        assert cpu == 100
        assert mem == 1
        assert swap == 50

    def test_version_string_exists(self):
        from core.config import __version__
        assert isinstance(__version__, str)
        assert len(__version__) > 0


# ── macOS integration tests (require darwin) ─────────────────────────────────

@pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
class TestMacOSIntegration:
    def test_get_stats_keys(self):
        from core import get_stats
        stats = get_stats()
        for key in ('cpu', 'mem', 'swap', 'mem_total_gb', 'pressure_status', 'lag_risk'):
            assert key in stats, f"Missing key: {key}"

    def test_get_stats_cpu_in_range(self):
        from core import get_stats
        stats = get_stats()
        assert 0.0 <= stats['cpu'] <= 100.0

    def test_get_stats_mem_in_range(self):
        from core import get_stats
        stats = get_stats()
        assert 0.0 <= stats['mem'] <= 100.0

    def test_get_stats_swap_in_range(self):
        from core import get_stats
        stats = get_stats()
        assert 0.0 <= stats['swap'] <= 100.0

    def test_get_stats_total_gb_positive(self):
        from core import get_stats
        stats = get_stats()
        assert stats['mem_total_gb'] > 0

    def test_pressure_status_valid(self):
        from core import get_memory_pressure
        status, val = get_memory_pressure()
        assert status in ("OK", "WARN", "HIGH", "UNKNOWN")
        assert isinstance(val, int)

    def test_check_thresholds_returns_list(self):
        from core import check_thresholds, get_stats
        import core as core_module
        core_module._last_alert = {}
        stats = get_stats()
        alerts = check_thresholds(stats, cpu_limit=0, mem_limit=0, swap_limit=0)
        assert isinstance(alerts, list)

    def test_get_combined_process_info_structure(self):
        from core import get_combined_process_info
        cpu_procs, mem_procs, gpu_procs = get_combined_process_info(limit=3)
        assert isinstance(cpu_procs, list)
        assert isinstance(mem_procs, list)
        assert len(cpu_procs) <= 3
        if cpu_procs:
            p = cpu_procs[0]
            assert 'pid' in p
            assert 'cpu' in p
            assert 'mem' in p
            assert 'name' in p

    def test_platform_guard(self):
        """main.py must reject non-darwin platforms."""
        import importlib
        import main
        with patch.object(sys, 'platform', 'linux'):
            with pytest.raises(SystemExit):
                main.main()
