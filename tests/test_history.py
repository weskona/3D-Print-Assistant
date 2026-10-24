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


def test_energy_from_meter_delta():
    h = PrintHistory()
    h.update_status("idle", "running", T0, "x")
    h.session.energy_start_kwh = 10.0
    rec = h.finish("finish", T0 + timedelta(hours=1), 100, None, 20, None, 10.5, 0.30)
    assert rec.energy_kwh == 0.5
    assert rec.energy_cost == 0.15
    assert rec.filament_cost == 2.0
    assert rec.cost == 2.15
    assert h.total_energy_kwh == 0.5


def test_energy_from_power_integration():
    h = PrintHistory()
    h.update_status("idle", "running", T0, "x")
    h.session.add_power(T0, 100)
    h.session.add_power(T0 + timedelta(hours=1), 200)
    rec = h.finish("finish", T0 + timedelta(hours=2), 0, None, 20, None, None, 0.5)
    assert rec.energy_kwh == 0.3  # 100W*1h + 200W*1h
    assert rec.energy_cost == 0.15


def test_parse_and_lookup_prices():
    from druck_assistant.history import parse_prices, price_for

    prices = parse_prices("PLA=20\npetg = 24,5; PLA-CF=32")
    assert prices == {"PLA": 20.0, "PETG": 24.5, "PLA-CF": 32.0}
    assert price_for("pla", prices, 25) == 20.0
    assert price_for("PLA-CF", prices, 25) == 32.0
    assert price_for("PLA Basic", prices, 25) == 20.0
    assert price_for("ABS", prices, 25) == 25
    assert price_for(None, prices, 25) == 25
    for bad in ("PLA", "=5", "PLA=abc", "PLA=-1"):
        try:
            parse_prices(bad)
        except ValueError:
            continue
        raise AssertionError(bad)
