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
for name in ("const", "catalog", "consumption", "history", "spools"):
    spec = importlib.util.spec_from_file_location(f"druck_assistant.{name}", PKG / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"druck_assistant.{name}"] = mod
    spec.loader.exec_module(mod)

from druck_assistant.catalog import color_index, load_catalog  # noqa: E402
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


def test_renaming_a_print_keeps_everything_else():
    h = PrintHistory()
    h.update_status("idle", "running", T0, "Wrong name")
    rec = h.finish("finish", T0 + timedelta(hours=1), 100, None, 20)
    before = dict(h.find(rec.started))
    renamed = h.rename(rec.started, "Benchy")
    assert renamed["name"] == "Benchy"
    assert {**renamed, "name": before["name"]} == before
    try:
        h.rename("missing", "x")
    except KeyError:
        pass
    else:
        raise AssertionError("unknown print")


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


def test_replacement_is_the_closest_color_then_the_fullest_stock_spool():
    store = SpoolStore()
    low = store.save_spool({"name": "Bambu PETG Basic", "material": "PETG", "color": "#000000", "remaining_g": 20})
    store.save_spool({"name": "Bambu PETG HF", "material": "PETG", "color": "#000000"})  # other variant
    store.save_spool({"name": "Bambu PETG Basic #2", "material": "PETG", "color": "#ffffff"})  # other color
    half = store.save_spool({"name": "Bambu PETG Basic #3", "material": "PETG", "color": "#000000", "remaining_g": 400})
    full = store.save_spool({"name": "Bambu PETG Basic #4", "material": "PETG", "color": "#010101"})
    assert store.replacement_for(low).id == half.id  # identical color wins
    store.assign("p:t1", half.id)
    assert store.replacement_for(low).id == full.id
    store.archive(full.id)
    assert store.replacement_for(low) is None


def _tray(name="Bambu PLA Matte", color="#950051FF", uuid="A" * 32):
    return {"name": name, "type": "PLA", "color": color, "tray_uuid": uuid, "tray_weight": "1000", "remain": 50, "remain_enabled": True}


def test_new_bambu_spool_gets_the_catalog_color_in_its_notes():
    store = SpoolStore()
    store.colors = color_index(load_catalog())
    action, spool = store.import_slot("p:t1", _tray(), include_untagged=False)
    assert action == "created" and spool.notes == "Plum (11204)"
    # a color that is not in the catalog leaves the notes empty
    _, other = store.import_slot("p:t2", _tray(color="#123456FF", uuid="B" * 32), include_untagged=False)
    assert other.notes == ""


def test_backfill_fills_only_empty_notes_of_bambu_spools():
    store = SpoolStore()
    store.colors = color_index(load_catalog())
    auto = store.save_spool({"name": "Bambu PLA Matte #2", "material": "PLA", "color": "#950051", "rfid": "C" * 32, "brand": "Bambu Lab"})
    own = store.save_spool({"name": "Bambu PLA Matte", "material": "PLA", "color": "#950051", "brand": "Bambu Lab", "notes": "mine"})
    third = store.save_spool({"name": "Anycubic PLA+", "material": "PLA", "color": "#950051"})
    assert store.backfill_notes() == 1
    assert (auto.notes, own.notes, third.notes) == ("Plum (11204)", "mine", "")
    assert store.backfill_notes() == 0


def _used(store, spool, grams):
    store.consume(spool.id, grams)


def test_weighing_teaches_the_correction_factor():
    store = SpoolStore()
    spool = store.save_spool({"name": "Bambu PLA Basic", "material": "PLA", "brand": "Bambu Lab"})
    assert spool.anchor_g == 1000  # a new full spool is its own anchor
    _used(store, spool, 100)
    assert spool.remaining_g == 900 and spool.used_since_anchor_g == 100
    # the scale says 780 g of filament are left: the prints booked 100 g, in truth 220 g were used
    store.weigh(spool.id, 780 + spool.tare)
    assert store.last_sample == {"spool_id": spool.id, "slicer_g": 100, "actual_g": 220, "at": store.last_sample["at"]}
    assert spool.anchor_g == 780 and spool.used_since_anchor_g == 0 and spool.weighed_at
    assert store.suggested_factor() is None  # needs three samples

    for _ in range(2):
        _used(store, spool, 100)
        store.weigh(spool.id, spool.anchor_g - 130 + spool.tare)
    factor, n = store.suggested_factor()
    assert n == 3 and 1.3 < factor < 1.6
    store.set_usage_factor(factor)
    before = spool.remaining_g
    _used(store, spool, 100)
    assert round(before - spool.remaining_g, 1) == round(100 * store.usage_factor, 1)
    store.restore(spool.id, 100)
    assert spool.remaining_g == before and spool.used_since_anchor_g == 0


def test_a_small_use_or_a_guessed_amount_gives_no_sample_and_an_edit_resets_the_anchor():
    store = SpoolStore()
    spool = store.save_spool({"name": "Bambu PLA Basic", "material": "PLA", "brand": "Bambu Lab"})
    _used(store, spool, 20)
    store.weigh(spool.id, 900 + spool.tare)
    assert store.last_sample is None and store.calibration == []  # under 50 g

    _used(store, spool, 80)
    spool = store.save_spool({**spool.as_dict(), "remaining_g": 500})  # typed in by hand
    assert spool.anchor_g is None and spool.used_since_anchor_g == 0
    store.weigh(spool.id, 480 + spool.tare)
    assert store.last_sample is None and spool.anchor_g == 480

    partial = store.save_spool({"name": "Bambu PLA Basic", "material": "PLA", "remaining_g": 400})
    assert partial.anchor_g is None  # a partial amount typed in is not an anchor
    flagged = store.save_spool({"name": "Bambu PETG", "material": "PETG"})
    store._sync_remaining(flagged, {"remain": 3, "remain_enabled": True})
    assert flagged.estimated and flagged.anchor_g is None


def test_the_factor_is_kept_in_range_and_saved():
    store = SpoolStore()
    assert store.set_usage_factor(5) == 1.5 and store.set_usage_factor("x") == 1.0
    store.set_usage_factor(1.2)
    again = SpoolStore(**store.to_dict())
    assert again.usage_factor == 1.2


def test_tare_comes_from_the_spool_then_its_type_then_the_brand_then_the_default():
    store = SpoolStore()
    bambu = store.save_spool({"name": "Bambu PLA Basic", "material": "PLA", "brand": "Bambu Lab"})
    other = store.save_spool({"name": "Anycubic PLA+", "material": "PLA", "brand": "Anycubic"})
    assert store.tare_of(bambu) == (250.0, "default") and store.tare_of(other) == (200.0, "default")

    store.set_settings({"tare_defaults": {"Bambu Lab": 245, "": 180}})
    assert store.tare_of(bambu) == (245.0, "brand") and store.tare_of(other) == (180.0, "brand")

    store.set_settings({"tare_presets": [{"name": "Self-printed spool", "tare_g": 78}]})
    preset = store.tare_presets[0]
    bambu = store.save_spool({**bambu.as_dict(), "tare_preset": preset["id"]})
    assert store.tare_of(bambu) == (78.0, "preset")
    assert store.spool_dict(bambu)["tare_effective_g"] == 78.0

    # weighing uses the type; the unchanged tare is not pinned to the spool, a different one is
    store.weigh(bambu.id, 478, tare_g=78)
    assert bambu.remaining_g == 400 and bambu.tare_g is None
    store.weigh(bambu.id, 478, tare_g=70)
    assert bambu.tare_g == 70 and bambu.remaining_g == 408 and store.tare_of(bambu) == (70.0, "spool")

    # deleting a type releases the spools that used it
    other = store.save_spool({**other.as_dict(), "tare_preset": preset["id"]})
    store.set_settings({"tare_presets": []})
    assert store.spools[other.id].tare_preset == ""


def test_settings_are_validated_and_saved():
    store = SpoolStore()
    try:
        store.set_settings({"tare_presets": [{"name": " ", "tare_g": 50}]})
        raise AssertionError("expected an error")
    except SpoolError:
        pass
    store.set_settings({"options": {"weigh_remind_g": 40, "unknown": 1}})
    assert store.options == {"weigh_remind_g": 40.0, "ams_diff_points": 15.0, "catalog_auto": 0.0}
    again = SpoolStore(**store.to_dict())
    assert again.options["weigh_remind_g"] == 40.0


def test_weighing_can_pick_the_spool_type():
    store = SpoolStore()
    store.set_settings({"tare_presets": [{"name": "Self-printed", "tare_g": 78}]})
    preset = store.tare_presets[0]
    spool = store.save_spool({"name": "Bambu PLA Basic", "material": "PLA", "brand": "Bambu Lab", "tare_g": 99})
    store.weigh(spool.id, 478, tare_preset=preset["id"])
    assert spool.tare_preset == preset["id"] and spool.tare_g is None and spool.remaining_g == 400
    store.weigh(spool.id, 478 - 78 + 250, tare_preset="")  # back to the brand default
    assert spool.tare_preset == "" and spool.remaining_g == 400
    try:
        store.weigh(spool.id, 400, tare_preset="nope")
        raise AssertionError("expected an error")
    except SpoolError:
        pass


def test_projects_group_prints_and_a_print_belongs_to_one_project():
    store = SpoolStore()
    a = store.save_project({"name": " Garden box ", "notes": "PETG"})
    b = store.save_project({"name": "Robot"})
    assert a["name"] == "Garden box" and a["created"] and a["prints"] == []
    store.assign_prints(a["id"], ["p1|t1", "p1|t2", "p1|t1"])
    assert a["prints"] == ["p1|t1", "p1|t2"]
    store.assign_prints(b["id"], ["p1|t2"])  # moves the print
    assert a["prints"] == ["p1|t1"] and b["prints"] == ["p1|t2"]
    store.assign_prints(None, ["p1|t1"])  # out of every project
    assert a["prints"] == []

    renamed = store.save_project({"id": b["id"], "name": "Robot v2"})
    assert renamed is b and b["name"] == "Robot v2" and b["prints"] == ["p1|t2"]
    again = SpoolStore(**store.to_dict())
    assert [p["name"] for p in again.projects] == ["Garden box", "Robot v2"] and again.projects[1]["prints"] == ["p1|t2"]

    store.delete_project(a["id"])
    assert [p["id"] for p in store.projects] == [b["id"]]
    for call in (lambda: store.save_project({"name": " "}), lambda: store.save_project({"id": "x", "name": "n"}),
                 lambda: store.delete_project("x"), lambda: store.assign_prints("x", ["k"])):
        try:
            call()
            raise AssertionError("expected an error")
        except SpoolError:
            pass
