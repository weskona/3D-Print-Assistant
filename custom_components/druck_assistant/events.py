"""Home Assistant independent event log: what the assistant noticed, newest last."""

from __future__ import annotations

from typing import Any

MAX_EVENTS = 200

# What of an event is kept; the rest (the whole print record, for one) is not needed to show a line.
KEPT = (
    "serial", "name", "print", "spool", "slot", "action", "material", "type", "result",
    "weight_g", "cost", "duration_min", "remain", "remaining_g", "stock_g", "minimum_g",
    "needed_g", "available_g", "missing_g", "spools", "prints", "replacement",
)


class EventLog:
    def __init__(self, entries: list[dict[str, Any]] | None = None) -> None:
        self.entries: list[dict[str, Any]] = list(entries or [])[-MAX_EVENTS:]

    def add(self, kind: str, data: dict[str, Any], time: str) -> dict[str, Any]:
        entry = {"time": time, "kind": kind}
        for key in KEPT:
            value = data.get(key)
            if isinstance(value, (str, int, float, bool)):
                entry[key] = value
        self.entries.append(entry)
        del self.entries[:-MAX_EVENTS]
        return entry

    def recent(self, count: int = 100) -> list[dict[str, Any]]:
        """The newest entries, newest first."""
        return self.entries[::-1][:count]

    def clear(self) -> None:
        self.entries.clear()
