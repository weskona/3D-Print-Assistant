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


def test_spool_store():
    import importlib.util as iu

    spec = iu.spec_from_file_location("druck_assistant.spools", PKG / "spools.py")
    spools = iu.module_from_spec(spec)
    sys.modules["druck_assistant.spools"] = spools
    spec.loader.exec_module(spools)

    store = spools.SpoolStore()
    a = store.save_spool({"name": "Red PLA", "material": "PLA", "price_per_kg": "20", "color": "#ff0000"})
    b = store.save_spool({"name": "Black PETG", "material": "PETG", "initial_weight_g": 500})
    assert a.remaining_g == 1000 and b.remaining_g == 500 and b.price_per_kg is None

    store.assign("p:ams1:tray_1", a.id)
    store.assign("p:ams1:tray_2", a.id)  # a spool sits in one slot only
    assert list(store.assignments) == ["p:ams1:tray_2"]
    assert store.spool_for_slot("p:ams1:tray_2").id == a.id
    assert store.spool_for_slot("nope") is None

    store.consume(a.id, 950)
    assert store.spools[a.id].remaining_g == 50
    store.consume(a.id, 500)
    assert store.spools[a.id].remaining_g == 0
    assert [s.id for s in store.low_spools(15)] == [a.id]

    updated = store.save_spool({"id": a.id, "name": "Red PLA", "material": "PLA", "remaining_g": 800})
    assert updated.remaining_g == 800
    assert not store.low_spools(15)

    restored = spools.SpoolStore(**store.to_dict())
    assert restored.assignments == store.assignments

    store.delete_spool(a.id)
    assert not store.assignments
    for bad in ({"name": "", "material": "PLA"}, {"name": "x", "material": "PLA", "color": "red"},
                {"name": "x", "material": "PLA", "initial_weight_g": 0}, {"id": "zzz", "name": "x", "material": "PLA"},
                {"name": "x", "material": "PLA", "price_per_kg": -1}):
        try:
            store.save_spool(bad)
        except spools.SpoolError:
            continue
        raise AssertionError(bad)


def _spools_module():
    import importlib.util as iu

    spec = iu.spec_from_file_location("druck_assistant.spools", PKG / "spools.py")
    mod = iu.module_from_spec(spec)
    sys.modules["druck_assistant.spools"] = mod
    spec.loader.exec_module(mod)
    return mod


TRAY = {
    "type": "PLA", "name": "Bambu PLA Basic", "color": "#FF0000FF", "tray_weight": 1000,
    "remain": 80, "remain_enabled": True, "empty": False,
    "tray_uuid": "A1B2C3D4E5F60718293A4B5C6D7E8F90", "tag_uid": "0123456789ABCDEF",
}
BLANK = "0" * 32


def test_import_rfid_spool_and_recognize_it_in_another_slot():
    m = _spools_module()
    store = m.SpoolStore()
    action, spool = store.import_slot("p:t1", TRAY, include_untagged=False)
    assert action == "created"
    assert (spool.material, spool.brand, spool.remaining_g, spool.initial_weight_g) == ("PLA", "Bambu Lab", 800.0, 1000.0)
    assert spool.color == "#FF0000FF" and store.assignments == {"p:t1": spool.id}

    assert store.import_slot("p:t1", TRAY, include_untagged=False)[0] == "skipped"  # no duplicate
    action, again = store.import_slot("p:t2", TRAY, include_untagged=False)  # moved to slot 2
    assert action == "assigned" and again.id == spool.id
    assert store.assignments == {"p:t2": spool.id} and len(store.spools) == 1


def test_import_untagged_only_on_manual_import():
    m = _spools_module()
    store = m.SpoolStore()
    raw = {**TRAY, "tray_uuid": BLANK, "tag_uid": BLANK, "name": "Generic PETG", "type": "PETG"}
    assert store.import_slot("p:t3", raw, include_untagged=False) == ("skipped", None)
    action, spool = store.import_slot("p:t3", raw, include_untagged=True)
    assert action == "created" and spool.rfid == "" and spool.brand == ""
    assert store.import_slot("p:t3", raw, include_untagged=True)[0] == "skipped"  # slot already has a spool


def test_import_adopts_manual_spool_and_skips_empty_slots():
    m = _spools_module()
    store = m.SpoolStore()
    mine = store.save_spool({"name": "Mine", "material": "PLA"})
    store.assign("p:t1", mine.id)
    action, spool = store.import_slot("p:t1", TRAY, include_untagged=False)
    assert action == "adopted" and spool.id == mine.id and spool.rfid == TRAY["tray_uuid"]
    assert len(store.spools) == 1
    assert store.import_slot("p:t9", {**TRAY, "empty": True}, include_untagged=True)[0] == "skipped"
    assert store.import_slot("p:t9", {"type": "", "empty": False}, include_untagged=True)[0] == "skipped"
    # editing keeps the tag
    edited = store.save_spool({"id": mine.id, "name": "Renamed", "material": "PLA"})
    assert edited.rfid == TRAY["tray_uuid"]


def test_import_unknown_remaining_uses_full_spool():
    m = _spools_module()
    store = m.SpoolStore()
    _, spool = store.import_slot("p:t1", {**TRAY, "remain": -1}, include_untagged=False)
    assert spool.remaining_g == 1000.0


def test_archive_and_restore():
    m = _spools_module()
    store = m.SpoolStore()
    spool = store.save_spool({"name": "Empty", "material": "PLA", "initial_weight_g": 100})
    store.assign("p:t1", spool.id)
    store.consume(spool.id, 100)
    assert store.spools[spool.id].remaining_g == 0

    store.archive(spool.id)
    assert store.spools[spool.id].archived and not store.assignments  # leaves its slot
    assert not store.low_spools(15)
    try:
        store.assign("p:t1", spool.id)
    except m.SpoolError:
        pass
    else:
        raise AssertionError("archived spools cannot be assigned")

    # editing keeps the archive flag and survives a storage round trip
    store.save_spool({"id": spool.id, "name": "Empty 2", "material": "PLA"})
    assert store.spools[spool.id].archived
    assert m.SpoolStore(**store.to_dict()).spools[spool.id].archived

    store.archive(spool.id, False)
    store.assign("p:t1", spool.id)
    assert store.assignments == {"p:t1": spool.id}


def test_archived_rfid_spool_is_not_restored_or_duplicated_by_import():
    m = _spools_module()
    store = m.SpoolStore()
    _, spool = store.import_slot("p:t1", TRAY, include_untagged=True)
    store.archive(spool.id)
    # the emptied spool is still in the AMS: neither auto nor manual import brings it back
    for manual in (False, True):
        assert store.import_slot("p:t1", TRAY, include_untagged=manual) == ("skipped", spool)
    assert len(store.spools) == 1 and spool.archived and not store.assignments


def test_four_pack_is_matched_by_new_rfid_spools():
    m = _spools_module()
    store = m.SpoolStore()
    pack = store.add_spools({"name": "PETG Basic Black", "material": "PETG", "color": "#101010", "price_per_kg": 18}, 4)
    assert [s.name for s in pack][:2] == ["PETG Basic Black #1", "PETG Basic Black #2"] and len(store.spools) == 4

    black = {**TRAY, "type": "PETG", "color": "#000000FF", "name": "Bambu PETG Basic"}
    action, first = store.import_slot("p:t1", {**black, "tray_uuid": "A" * 32}, include_untagged=False)
    assert action == "adopted" and first.id == pack[0].id and first.rfid == "A" * 32
    assert len(store.spools) == 4  # nothing new was created, 3 spools remain in stock

    # the next new tagged spool takes the next one; the first stays untouched
    _, second = store.import_slot("p:t2", {**black, "tray_uuid": "B" * 32}, include_untagged=False)
    assert second.id == pack[1].id and store.assignments == {"p:t1": first.id, "p:t2": second.id}
    stock = [s for s in store.spools.values() if not s.rfid and s.id not in store.assignments.values()]
    assert len(stock) == 2

    # the tagged spool is recognized by its tag from now on
    assert store.import_slot("p:t3", {**black, "tray_uuid": "A" * 32}, include_untagged=False)[1].id == first.id


def test_stock_matching_prefers_color_and_fullest_and_ignores_other_materials():
    m = _spools_module()
    store = m.SpoolStore()
    store.save_spool({"name": "White PETG", "material": "PETG", "color": "#ffffff"})
    store.save_spool({"name": "PLA Black", "material": "PLA", "color": "#000000"})
    used = store.save_spool({"name": "Black PETG used", "material": "PETG", "color": "#000000", "remaining_g": 300})
    full = store.save_spool({"name": "Black PETG full", "material": "PETG", "color": "#050505"})
    nocolor = store.save_spool({"name": "PETG no color", "material": "PETG"})

    tray = {**TRAY, "type": "PETG", "color": "#000000FF", "tray_uuid": "C" * 32}
    # closest color first (exact black beats #050505), even if the other one is fuller
    assert store.find_stock(tray).id == used.id
    store.archive(used.id)
    assert store.find_stock(tray).id == full.id
    store.assign("p:x", full.id)
    assert store.find_stock(tray).id == nocolor.id  # unknown color is a weak match
    store.archive(nocolor.id)
    assert store.find_stock(tray) is None  # white is too far, PLA is another material
    action, created = store.import_slot("p:t1", tray, include_untagged=False)
    assert action == "created"


def test_untagged_tray_uses_stock_on_manual_import():
    m = _spools_module()
    store = m.SpoolStore()
    mine = store.save_spool({"name": "Generic PLA", "material": "PLA", "color": "#ff0000"})
    raw = {**TRAY, "tray_uuid": BLANK, "tag_uid": BLANK, "type": "PLA", "color": "#FF0000FF"}
    assert store.import_slot("p:t1", raw, include_untagged=False) == ("skipped", None)
    action, spool = store.import_slot("p:t1", raw, include_untagged=True)
    assert action == "assigned" and spool.id == mine.id and spool.rfid == "" and len(store.spools) == 1


def test_add_spools_validates_quantity():
    m = _spools_module()
    store = m.SpoolStore()
    for bad in (0, 51):
        try:
            store.add_spools({"name": "x", "material": "PLA"}, bad)
        except m.SpoolError:
            continue
        raise AssertionError(bad)
    assert len(store.add_spools({"name": "x", "material": "PLA"}, 1)) == 1


def test_manual_correction_moves_the_tag_and_survives_auto_import():
    m = _spools_module()
    store = m.SpoolStore()
    pack = store.add_spools({"name": "Black", "material": "PETG", "color": "#101010"}, 2)
    right = store.save_spool({"name": "Black Matte", "material": "PETG", "color": "#202020"})
    tray = {**TRAY, "type": "PETG", "color": "#000000FF", "tray_uuid": "D" * 32}

    _, wrong = store.import_slot("p:t1", tray, include_untagged=False)
    assert wrong.id == pack[0].id and wrong.rfid == "D" * 32

    # the user corrects it in the panel: the tag follows the chosen spool
    store.assign("p:t1", right.id, tray["tray_uuid"])
    assert right.rfid == "D" * 32 and wrong.rfid == "" and store.assignments == {"p:t1": right.id}
    # the wrongly matched spool is plain stock again and a later import keeps the correction
    assert store.import_slot("p:t1", tray, include_untagged=False) == ("skipped", right)
    assert store.assignments == {"p:t1": right.id}


def test_clearing_a_slot_stops_auto_assignment_until_manual_import():
    m = _spools_module()
    store = m.SpoolStore()
    tray = {**TRAY, "tray_uuid": "E" * 32}
    _, spool = store.import_slot("p:t1", tray, include_untagged=False)
    store.assign("p:t1", None, tray["tray_uuid"])
    assert not store.assignments
    assert store.import_slot("p:t1", tray, include_untagged=False) == ("skipped", None)
    assert not store.assignments and len(store.spools) == 1
    assert m.SpoolStore(**store.to_dict()).dismissed_rfids == {"E" * 32}  # persisted

    action, again = store.import_slot("p:t1", tray, include_untagged=True)  # button overrides
    assert action == "assigned" and again.id == spool.id and not store.dismissed_rfids


def test_editing_the_tag_keeps_it_unique():
    m = _spools_module()
    store = m.SpoolStore()
    a = store.save_spool({"name": "A", "material": "PLA", "rfid": "F" * 32})
    b = store.save_spool({"name": "B", "material": "PLA"})
    store.save_spool({"id": b.id, "name": "B", "material": "PLA", "rfid": "F" * 32})
    assert store.spools[b.id].rfid == "F" * 32 and store.spools[a.id].rfid == ""
    store.save_spool({"id": b.id, "name": "B", "material": "PLA", "rfid": ""})  # unlink
    assert store.spools[b.id].rfid == "" and store.find_by_rfid("F" * 32) is None


def test_live_energy_estimate_does_not_change_the_session():
    from druck_assistant.history import PrintSession

    s = PrintSession(started=T0)
    s.add_power(T0, 200)
    # power only: 200 W for 30 min since the last reading = 0.1 kWh, nothing is stored
    assert abs(s.estimate_energy_kwh(T0 + timedelta(minutes=30), None) - 0.1) < 1e-9
    assert s.energy_acc_kwh == 0 and s.power_ts == T0
    s.add_power(T0 + timedelta(hours=1), 100)
    assert abs(s.estimate_energy_kwh(T0 + timedelta(hours=2), None) - (0.2 + 0.1)) < 1e-9
    # a meter wins over the power estimate
    s.energy_start_kwh = 10.0
    assert abs(s.estimate_energy_kwh(T0 + timedelta(hours=2), 10.4) - 0.4) < 1e-9


def test_duration_sensor_values_are_converted_to_minutes():
    from druck_assistant.history import to_minutes

    # ha-bambulab: native minutes, displayed in hours -> 1.867 h is 1 h 52 min
    assert round(to_minutes(1.8667, "h")) == 112
    assert to_minutes(112, "min") == 112
    assert to_minutes(6720, "s") == 112
    assert to_minutes(0.5, "d") == 720
    assert to_minutes(112, None) == 112 and to_minutes(112, "weeks") == 112  # unknown unit: as is
    assert to_minutes(None, "h") is None


def test_cost_split_in_totals_handles_older_records():
    from druck_assistant.history import PrintHistory

    h = PrintHistory([
        {"name": "old", "result": "finish", "weight_g": 100, "cost": 2.0},  # before the split: filament only
        {"name": "new", "result": "finish", "weight_g": 50, "cost": 1.5, "filament_cost": 1.0, "energy_cost": 0.5, "energy_kwh": 1.7},
    ])
    assert h.total_cost == 3.5
    assert h.total_filament_cost == 3.0  # 2.0 + 1.0
    assert h.total_energy_cost == 0.5
    assert round(h.total_filament_cost + h.total_energy_cost, 2) == h.total_cost
