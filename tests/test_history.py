"""Tests for the HA independent print history logic."""

import importlib.util
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

PKG = Path(__file__).parent.parent / "custom_components" / "druck_assistant"
pkg = types.ModuleType("druck_assistant")
pkg.__path__ = [str(PKG)]
sys.modules["druck_assistant"] = pkg
for name in ("const", "history"):
    spec = importlib.util.spec_from_file_location(f"druck_assistant.{name}", PKG / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"druck_assistant.{name}"] = mod
    spec.loader.exec_module(mod)

from druck_assistant.history import PrintHistory, calculate_cost  # noqa: E402

T0 = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)


def test_cost():
    assert calculate_cost(100, 25) == 2.5
    assert calculate_cost(None, 25) == 0.0


def test_successful_print():
    h = PrintHistory()
    assert h.update_status("idle", "running", T0, "Benchy") == "started"
    assert h.update_status("running", "pause", T0) is None
    assert h.update_status("pause", "running", T0) is None
    assert h.update_status("running", "finish", T0) == "finish"
    rec = h.finish("finish", T0 + timedelta(minutes=90), 40, {"AMS A1": 40}, 20)
    assert rec.duration_min == 90.0
    assert rec.cost == 0.8
    assert h.total_prints == 1 and h.successful_prints == 1
    assert h.total_weight_g == 40.0


def test_aborted_print_counts_as_failed():
    h = PrintHistory()
    h.update_status("idle", "running", T0, "x")
    assert h.update_status("running", "idle", T0) == "failed"
    h.finish("failed", T0 + timedelta(minutes=5), 3, None, 20)
    assert h.total_prints == 1 and h.successful_prints == 0


def test_finish_without_session_ignored():
    h = PrintHistory()
    assert h.update_status("idle", "finish", T0) is None
    assert h.finish("finish", T0, 1, None, 1) is None
