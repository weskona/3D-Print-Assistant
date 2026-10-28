"""Tests for the split of a print's filament over several spools."""

import importlib.util
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

PKG = Path(__file__).parent.parent / "custom_components" / "druck_assistant"
pkg = types.ModuleType("druck_assistant")
pkg.__path__ = [str(PKG)]
sys.modules["druck_assistant"] = pkg
for name in ("const", "consumption", "history"):
    spec = importlib.util.spec_from_file_location(f"druck_assistant.{name}", PKG / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"druck_assistant.{name}"] = mod
    spec.loader.exec_module(mod)

from druck_assistant.consumption import (  # noqa: E402
    Segment,
    SlotInfo,
    UsageTracker,
    measured_grams,
    split_usage,
)
from druck_assistant.history import PrintHistory  # noqa: E402

T0 = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)


def grams(usages):
    return {u.slot: u.grams for u in usages}


def test_single_slot_uses_the_whole_weight_when_finished():
    out = split_usage(50, finished=True, progress=100, segments=[Segment("a", 0)], slots={"a": SlotInfo("a", "PLA")})
    assert grams(out) == {"a": 50}


def test_a_failed_print_counts_only_for_its_progress():
    out = split_usage(50, finished=False, progress=40, segments=[Segment("a", 0)], slots={})
    assert grams(out) == {"a": 20}
    # without any progress information the whole weight counts, as before
    assert grams(split_usage(50, finished=False, progress=None, segments=[Segment("a", 0)], slots={})) == {"a": 50}


def test_multi_color_with_the_planned_grams_per_slot():
    slots = {"a": SlotInfo("a", "PLA"), "b": SlotInfo("b", "PETG")}
    segments = [Segment("a", 0), Segment("b", 30), Segment("a", 60)]
    out = split_usage(60, finished=True, progress=100, segments=segments, slots=slots, plan={"a": 40, "b": 20})
    assert grams(out) == {"a": 40, "b": 20}
    # a print stopped at half way: every planned amount is halved
    out = split_usage(60, finished=False, progress=50, segments=segments, slots=slots, plan={"a": 40, "b": 20})
    assert grams(out) == {"a": 20, "b": 10}


def test_a_spool_that_runs_empty_hands_the_rest_to_the_refill_spool():
    slots = {
        "a": SlotInfo("a", "PETG", capacity_g=30),
        "b": SlotInfo("b", "PETG", capacity_g=500),
    }
    segments = [Segment("a", 0), Segment("b", 25)]
    # planned for slot a only, the AMS continued with b
    out = split_usage(100, finished=True, progress=100, segments=segments, slots=slots, plan={"a": 100})
    assert grams(out) == {"a": 30, "b": 70}
    # without a plan the single filament total is filled the same way
    out = split_usage(100, finished=True, progress=100, segments=segments, slots=slots)
    assert grams(out) == {"a": 30, "b": 70}


def test_measured_remaining_percent_decides_the_split_when_known():
    slots = {
        "a": SlotInfo("a", "PETG", capacity_g=100, measured_g=40),
        "b": SlotInfo("b", "PETG", capacity_g=900, measured_g=60),
    }
    out = split_usage(100, finished=True, progress=100, segments=[Segment("a", 0), Segment("b", 50)], slots=slots)
    assert grams(out) == {"a": 40, "b": 60}


def test_without_capacity_or_measurement_the_progress_shares_decide():
    slots = {"a": SlotInfo("a", "PLA"), "b": SlotInfo("b", "PLA")}
    out = split_usage(100, finished=True, progress=100, segments=[Segment("a", 0), Segment("b", 60)], slots=slots)
    assert grams(out) == {"a": 60, "b": 40}


def test_measured_grams_needs_valid_readings():
    assert measured_grams(100, 70, 1000) == 300
    assert measured_grams(50, 60, 1000) == 0  # never negative
    assert measured_grams(-1, 70, 1000) is None  # unknown at the start
    assert measured_grams(100, 70, None) is None
    assert measured_grams(None, 70, 1000) is None


def test_usage_tracker_records_only_changes():
    t = UsageTracker()
    t.note("a", 0)
    t.note("a", 10)
    t.note(None, 20)
    t.note("b", 30)
    assert [(s.slot, s.start) for s in t.segments] == [("a", 0), ("b", 30)]


def test_history_charges_every_spool_with_its_own_price():
    h = PrintHistory()
    h.update_status("idle", "running", T0, "Mix")
    usages = [
        {"slot": "a", "spool_id": "s1", "spool_name": "Black", "weight_g": 30.0, "price_per_kg": 20.0},
        {"slot": "b", "spool_id": "s2", "spool_name": "White", "weight_g": 70.0, "price_per_kg": 10.0},
    ]
    rec = h.finish("finish", T0 + timedelta(hours=1), 100, None, 15, usages=usages, planned_g=100)
    assert rec.weight_g == 100.0 and rec.planned_g == 100
    assert rec.filament_cost == 1.3  # 0.60 + 0.70
    assert rec.price_per_kg == 13.0
    assert [u["cost"] for u in rec.usages] == [0.6, 0.7]
    assert rec.spool_id == "s1"


def test_history_single_spool_keeps_the_plain_record():
    h = PrintHistory()
    h.update_status("idle", "running", T0, "Benchy")
    usages = [{"slot": "a", "spool_id": "s1", "spool_name": "Black", "weight_g": 20.0, "price_per_kg": 25.0}]
    rec = h.finish("failed", T0 + timedelta(hours=1), 50, None, 25, usages=usages, planned_g=50)
    assert rec.weight_g == 20.0 and rec.planned_g == 50
    assert rec.usages == [] and rec.spool_id == "s1" and rec.filament_cost == 0.5
