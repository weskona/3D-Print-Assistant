"""The tracker's collection of slot data for the filament split (Home Assistant stubbed out)."""

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

PKG = Path(__file__).parent.parent / "custom_components" / "druck_assistant"


def _stub(name, **attrs):
    mod = types.ModuleType(name)
    mod.__dict__.update(attrs)
    sys.modules[name] = mod
    return mod


def _load_tracker():
    for name in (
        "homeassistant", "homeassistant.config_entries", "homeassistant.core",
        "homeassistant.helpers", "homeassistant.helpers.entity_registry",
        "homeassistant.helpers.dispatcher", "homeassistant.helpers.event",
        "homeassistant.helpers.storage", "homeassistant.util", "homeassistant.util.dt",
    ):
        _stub(name)
    sys.modules["homeassistant.helpers"].entity_registry = sys.modules["homeassistant.helpers.entity_registry"]
    sys.modules["homeassistant.util"].dt = sys.modules["homeassistant.util.dt"]
    sys.modules["homeassistant.config_entries"].ConfigEntry = object
    core = sys.modules["homeassistant.core"]
    core.Event = core.HomeAssistant = object
    core.callback = lambda f: f
    sys.modules["homeassistant.helpers.dispatcher"].async_dispatcher_send = lambda *a: None
    sys.modules["homeassistant.helpers.event"].async_track_state_change_event = lambda *a: None
    sys.modules["homeassistant.helpers.event"].async_call_later = lambda *a: None
    sys.modules["homeassistant.helpers.storage"].Store = object
    pkg = types.ModuleType("druck_assistant")
    pkg.__path__ = [str(PKG)]
    sys.modules["druck_assistant"] = pkg
    for name in ("const", "catalog", "consumption", "history", "spools", "tracker"):
        spec = importlib.util.spec_from_file_location(f"druck_assistant.{name}", PKG / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"druck_assistant.{name}"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["druck_assistant.tracker"], sys.modules["druck_assistant.spools"]


tracker_mod, spools_mod = _load_tracker()

A = "p:AMS_x_tray_1"
B = "p:AMS_x_tray_2"


def make_tracker(states):
    t = object.__new__(tracker_mod.PrintTracker)
    store = spools_mod.SpoolStore()
    t.filament = SimpleNamespace(store=store, changed=lambda: None)
    t.hass = SimpleNamespace(states=SimpleNamespace(get=lambda eid: states.get(eid)))
    t.slot_entities = lambda: {A: "sensor.ams_1_slot_1", B: "sensor.ams_1_slot_2"}
    t.price_for_material = lambda material: 12.0
    t._plan_attrs = {}
    t._state = lambda key: SimpleNamespace(attributes=t._plan_attrs) if key == "print_weight" else None
    return t, store


def slot_state(remain, active=False):
    return SimpleNamespace(attributes={"active": active, "remain": remain, "remain_enabled": True, "type": "PETG"})


def test_plan_attributes_are_mapped_to_slot_keys():
    t, _ = make_tracker({})
    t._plan_attrs = {"AMS 1 Tray 2": 12.5, "AMS 1 Tray 9": 3.0, "unit": "g", "flag": True}
    assert t._plan_by_slot() == {B: 12.5}


def test_spool_running_empty_is_split_between_both_spools():
    states = {"sensor.ams_1_slot_1": slot_state(100, True), "sensor.ams_1_slot_2": slot_state(100)}
    t, store = make_tracker(states)
    a = store.save_spool({"name": "Bambu PETG Basic", "material": "PETG", "remaining_g": 30, "price_per_kg": 20})
    b = store.save_spool({"name": "Bambu PETG Basic #2", "material": "PETG", "remaining_g": 500, "price_per_kg": 10})
    store.assign(A, a.id)
    store.assign(B, b.id)
    session = SimpleNamespace(
        start_slots=t._slot_snapshot(), slot_key=A, progress=100.0, plan={},
        usage=sys.modules["druck_assistant.consumption"].UsageTracker(),
    )
    session.usage.note(A, 0.0)
    session.usage.note(B, 25.0)  # the AMS continued with the second spool
    # no percent changes measurable (remain unchanged): the first spool is used up first
    usages = t._usages(session, "finish", 100.0)
    assert [(u["spool_id"], u["weight_g"], u["price_per_kg"]) for u in usages] == [
        (b.id, 70.0, 10.0),
        (a.id, 30.0, 20.0),
    ]


def test_a_print_that_is_already_running_gets_a_session_and_its_spool():
    from datetime import datetime, timedelta, timezone

    now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    started = now - timedelta(minutes=40)
    t, store = make_tracker({"sensor.ams_1_slot_1": slot_state(100, True), "sensor.ams_1_slot_2": slot_state(100)})
    spool = store.save_spool({"name": "Bambu PETG Basic", "material": "PETG", "price_per_kg": 12.34})
    store.assign(A, spool.id)
    t.history = sys.modules["druck_assistant.history"].PrintHistory()
    values = {"print_status": "running", "start_time": started.isoformat(), "subtask_name": "lid"}
    t._value = lambda key: values.get(key)
    t._float = lambda key: 40.0 if key == "print_progress" else None
    t._external_float = lambda key: None
    t._warn_shortage = lambda: None
    t.active_slot_key = lambda: A
    t._conf = lambda key: None
    t.hass.async_create_task = lambda coro: coro.close()
    tracker_mod.dt_util.utcnow = lambda: now

    t._ensure_session()
    session = t.history.session
    assert session is not None and session.started == started and session.name == "lid"
    assert session.spool_id == spool.id and session.slot_key == A
    assert session.usage.segments[0].slot == A and session.usage.segments[0].start == 40.0

    first = t.history.session
    t._ensure_session()  # an existing session is left alone
    assert t.history.session is first
    t.history.session = None
    values["print_status"] = "finish"
    t._ensure_session()  # nothing running, nothing to pick up
    assert t.history.session is None


def test_a_session_without_a_spool_adopts_the_spool_of_the_active_slot_later():
    from datetime import datetime, timezone

    t, store = make_tracker({"sensor.ams_1_slot_1": slot_state(100, True), "sensor.ams_1_slot_2": slot_state(100)})
    spool = store.save_spool({"name": "Bambu PETG Basic", "material": "PETG", "price_per_kg": 12.34})
    store.assign(A, spool.id)
    history = sys.modules["druck_assistant.history"].PrintHistory()
    history.session = sys.modules["druck_assistant.history"].PrintSession(started=datetime(2026, 1, 1, tzinfo=timezone.utc))
    t.history = history
    t._float = lambda key: 12.0 if key == "print_progress" else None
    t.active_slot_key = lambda: None  # the slots are not ready yet
    t._ensure_session()
    assert history.session.spool_id is None

    t.active_slot_key = lambda: A
    t._ensure_session()
    s = history.session
    assert (s.spool_id, s.spool_name, s.material, s.slot_key) == (spool.id, "Bambu PETG Basic", "PETG", A)
    assert s.start_slots and s.usage.segments[0].slot == A

    other = store.save_spool({"name": "Other", "material": "PETG"})
    store.assign(B, other.id)
    t.active_slot_key = lambda: B
    t._ensure_session()  # a spool that is known is never replaced
    assert history.session.spool_id == spool.id


def test_the_energy_meter_reading_at_the_start_comes_from_the_recorder():
    import asyncio
    from datetime import datetime, timedelta, timezone

    t, _ = make_tracker({})
    started = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    session = SimpleNamespace(energy_start_kwh=40.0)
    t.history = SimpleNamespace(session=session)
    t._conf = lambda key: "sensor.plug_energy"
    asked = {}

    class Instance:
        async def async_add_executor_job(self, job):
            return job()

    def get_significant_states(hass, start, end, entity_ids, **kwargs):
        asked.update(start=start, end=end, ids=entity_ids, **kwargs)
        return {"sensor.plug_energy": [SimpleNamespace(state="unavailable"), SimpleNamespace(state="35.5")]}

    recorder = types.ModuleType("homeassistant.components.recorder")
    recorder.get_instance = lambda hass: Instance()
    recorder.history = SimpleNamespace(get_significant_states=get_significant_states)
    sys.modules["homeassistant.components"] = types.ModuleType("homeassistant.components")
    sys.modules["homeassistant.components.recorder"] = recorder
    sys.modules["homeassistant.components"].recorder = recorder
    try:
        asyncio.run(t._backfill_energy(session, started))
        assert session.energy_start_kwh == 35.5  # the first usable reading, lower than the one taken after the restart
        assert asked["start"] == started and asked["end"] - started == timedelta(minutes=10) and asked["ids"] == ["sensor.plug_energy"] and asked["include_start_time_state"]

        session.energy_start_kwh = 30.0  # a reading above the current start value is not taken (meter reset)
        asyncio.run(t._backfill_energy(session, started))
        assert session.energy_start_kwh == 30.0
    finally:
        for name in ("homeassistant.components.recorder", "homeassistant.components"):
            sys.modules.pop(name, None)


def test_the_printer_start_time_is_only_used_when_it_is_plausible():
    from datetime import datetime, timedelta, timezone

    now = datetime(2026, 1, 2, 12, tzinfo=timezone.utc)
    t, _ = make_tracker({})
    values = {}
    t._value = lambda key: values.get(key)
    values["start_time"] = (now - timedelta(hours=2)).isoformat()
    assert t._printer_start(now) == now - timedelta(hours=2)
    for bad in ((now + timedelta(minutes=5)).isoformat(), (now - timedelta(hours=60)).isoformat(), "unknown", None, "2026-01-02T08:00:00"):
        values["start_time"] = bad
        assert t._printer_start(now) is None
