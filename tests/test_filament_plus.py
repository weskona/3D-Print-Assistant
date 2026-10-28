"""Weighing, rebooking, stock totals, shortage warnings and the extra spool fields."""

import importlib.util
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

PKG = Path(__file__).parent.parent / "custom_components" / "druck_assistant"
pkg = types.ModuleType("druck_assistant")
pkg.__path__ = [str(PKG)]
sys.modules["druck_assistant"] = pkg
for name in ("const", "consumption", "history", "spools"):
    spec = importlib.util.spec_from_file_location(f"druck_assistant.{name}", PKG / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"druck_assistant.{name}"] = mod
    spec.loader.exec_module(mod)

from druck_assistant.consumption import SlotInfo, shortages  # noqa: E402
from druck_assistant.history import PrintHistory  # noqa: E402
from druck_assistant.spools import SpoolError, SpoolStore, default_tare  # noqa: E402

T0 = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)


def test_weighing_sets_the_remaining_filament_from_the_gross_weight():
    store = SpoolStore()
    bambu = store.save_spool({"name": "A", "material": "PLA", "brand": "Bambu Lab"})
    assert default_tare("Bambu Lab") == 250 and default_tare("eSUN") == 200
    store.weigh(bambu.id, 850)
    assert bambu.remaining_g == 600
    store.weigh(bambu.id, 100)  # lighter than an empty spool: empty
    assert bambu.remaining_g == 0
    store.weigh(bambu.id, 5000)  # never above the full weight
    assert bambu.remaining_g == bambu.initial_weight_g
    store.weigh(bambu.id, 600, tare_g=180)  # the real empty weight is kept
    assert bambu.remaining_g == 420 and bambu.tare == 180
    for bad in ("x", -5):
        try:
            store.weigh(bambu.id, bad)
        except SpoolError:
            continue
        raise AssertionError(bad)


def test_extra_fields_are_validated_and_kept_on_update():
    store = SpoolStore()
    spool = store.save_spool({
        "name": "A", "material": "PETG", "purchased": "2026-10-01", "shop": " Shop ",
        "location": "Regal 2", "last_dried": "2026-10-20", "tare_g": 190,
    })
    assert (spool.purchased, spool.shop, spool.location, spool.tare_g) == ("2026-10-01", "Shop", "Regal 2", 190)
    again = store.save_spool({"id": spool.id, "name": "A2", "material": "PETG"})
    assert again.shop == "Shop" and again.last_dried == "2026-10-20" and again.tare_g == 190
    try:
        store.save_spool({"name": "B", "material": "PLA", "purchased": "yesterday"})
    except SpoolError:
        pass
    else:
        raise AssertionError("bad date")
    assert spool.as_dict()["tare_effective_g"] == 190


def test_restore_gives_filament_back_up_to_the_full_weight():
    store = SpoolStore()
    spool = store.save_spool({"name": "A", "material": "PLA", "remaining_g": 100})
    store.restore(spool.id, 50)
    assert spool.remaining_g == 150
    store.restore(spool.id, 5000)
    assert spool.remaining_g == 1000
    assert store.restore("nope", 10) is None


def test_stock_by_material_sums_active_spools():
    store = SpoolStore()
    store.save_spool({"name": "A", "material": "pla", "remaining_g": 300})
    store.save_spool({"name": "B", "material": "PLA", "remaining_g": 700})
    gone = store.save_spool({"name": "C", "material": "PLA", "remaining_g": 500})
    store.save_spool({"name": "D", "material": "PETG", "remaining_g": 100})
    store.archive(gone.id)
    assert store.stock_by_material() == {"PLA": 1000.0, "PETG": 100.0}


def test_rebooking_a_print_moves_the_filament_and_the_cost():
    h = PrintHistory()
    h.update_status("idle", "running", T0, "Benchy")
    rec = h.finish("finish", T0 + timedelta(hours=1), 100, None, 20)
    assert rec.filament_cost == 2.0 and rec.cost == 2.0
    previous, grams = h.rebook(rec.started, "new", "New spool", 30, "PETG", "#fff")
    assert previous is None and grams == 100
    stored = h.find(rec.started)
    assert stored["spool_id"] == "new" and stored["filament_cost"] == 3.0 and stored["cost"] == 3.0
    assert stored["material"] == "PETG"
    try:
        h.rebook("missing", "x", "x", 1)
    except KeyError:
        pass
    else:
        raise AssertionError("unknown print")
    stored["usages"] = [{"spool_id": "a"}, {"spool_id": "b"}]
    try:
        h.rebook(rec.started, "x", "x", 1)
    except ValueError:
        pass
    else:
        raise AssertionError("several spools")


def test_shortage_warning_names_a_refill_slot():
    slots = {
        "a": SlotInfo("a", "PETG", capacity_g=30),
        "b": SlotInfo("b", "PETG", capacity_g=500),
        "c": SlotInfo("c", "PLA", capacity_g=900),
    }
    out = shortages({"a": 100, "c": 50}, slots)
    assert out == [{"slot": "a", "needed_g": 100, "available_g": 30, "missing_g": 70, "refill_slot": "b"}]
    # the other PETG slot is too small as well: no refill is announced
    slots["b"].capacity_g = 10
    assert shortages({"a": 100}, slots)[0]["refill_slot"] is None
    # unknown capacity never warns
    assert shortages({"x": 100}, {"x": SlotInfo("x", "PLA")}) == []
