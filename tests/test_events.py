"""The event log keeps what a line needs and only the newest entries."""

import importlib.util
from pathlib import Path

PKG = Path(__file__).parent.parent / "custom_components" / "druck_assistant"
spec = importlib.util.spec_from_file_location("events", PKG / "events.py")
events = importlib.util.module_from_spec(spec)
spec.loader.exec_module(events)


def test_an_entry_keeps_only_the_known_plain_values():
    log = events.EventLog()
    entry = log.add("print_finished", {"name": "Benchy", "weight_g": 12.5, "filament": {"a": 1}, "usages": [1]}, "t")
    assert entry == {"time": "t", "kind": "print_finished", "name": "Benchy", "weight_g": 12.5}


def test_only_the_newest_entries_are_kept_and_listed_newest_first():
    log = events.EventLog()
    for i in range(events.MAX_EVENTS + 5):
        log.add("print_started", {"name": str(i)}, str(i))
    assert len(log.entries) == events.MAX_EVENTS
    assert [e["name"] for e in log.recent(2)] == [str(events.MAX_EVENTS + 4), str(events.MAX_EVENTS + 3)]
    assert len(events.EventLog(log.entries * 2).entries) == events.MAX_EVENTS


def test_clear_empties_the_log():
    log = events.EventLog([{"time": "t", "kind": "x"}])
    log.clear()
    assert log.recent() == []
