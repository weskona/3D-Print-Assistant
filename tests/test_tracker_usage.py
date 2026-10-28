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
    sys.modules["homeassistant.helpers.storage"].Store = object
    pkg = types.ModuleType("druck_assistant")
    pkg.__path__ = [str(PKG)]
    sys.modules["druck_assistant"] = pkg
    for name in ("const", "consumption", "history", "spools", "tracker"):
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
