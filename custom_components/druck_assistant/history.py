"""Home Assistant independent print session and history logic."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from .const import (
    ACTIVE_STATUSES,
    END_STATUSES,
    MAX_HISTORY,
    STATUS_FAILED,
    STATUS_RUNNING,
)


def calculate_cost(weight_g: float | None, price_per_kg: float) -> float:
    """Return the filament cost for a print."""
    if not weight_g or weight_g < 0:
        return 0.0
    return round(weight_g / 1000 * price_per_kg, 2)


@dataclass
class PrintRecord:
    """A completed (or failed) print."""

    name: str
    result: str
    started: str
    finished: str
    duration_min: float
    weight_g: float
    cost: float
    material: str | None = None
    color: str | None = None
    filament: dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PrintSession:
    """The print currently in progress."""

    started: datetime
    name: str | None = None
    material: str | None = None
    color: str | None = None


class PrintHistory:
    """Track print sessions from print_status transitions."""

    def __init__(self, records: list[dict[str, Any]] | None = None) -> None:
        self.records: list[dict[str, Any]] = list(records or [])
        self.session: PrintSession | None = None

    def update_status(
        self,
        old: str | None,
        new: str,
        now: datetime,
        name: str | None = None,
    ) -> str | None:
        """Handle a status change.

        Returns "started" when a session begins, the end status when a
        session ends, otherwise None.
        """
        if new == old:
            return None
        if new == STATUS_RUNNING and self.session is None:
            self.session = PrintSession(started=now, name=name)
            return "started"
        if new in ACTIVE_STATUSES:
            return None
        if new in END_STATUSES and self.session is not None:
            return new
        if new not in END_STATUSES:
            # Print aborted without a finish/failed state (idle, offline, ...).
            if self.session is not None and old in ACTIVE_STATUSES:
                return STATUS_FAILED
        return None

    def finish(
        self,
        result: str,
        now: datetime,
        weight_g: float | None,
        filament: dict[str, float] | None,
        price_per_kg: float,
        name: str | None = None,
    ) -> PrintRecord | None:
        """Close the session and store the record."""
        session, self.session = self.session, None
        if session is None:
            return None
        weight = float(weight_g or 0)
        record = PrintRecord(
            name=name or session.name or "unbekannt",
            result=result,
            started=session.started.isoformat(),
            finished=now.isoformat(),
            duration_min=round((now - session.started).total_seconds() / 60, 1),
            weight_g=weight,
            cost=calculate_cost(weight, price_per_kg),
            material=session.material,
            color=session.color,
            filament=dict(filament or {}),
        )
        self.records.append(record.as_dict())
        del self.records[:-MAX_HISTORY]
        return record

    @property
    def total_prints(self) -> int:
        return len(self.records)

    @property
    def successful_prints(self) -> int:
        return sum(1 for r in self.records if r["result"] != STATUS_FAILED)

    @property
    def total_weight_g(self) -> float:
        return round(sum(r["weight_g"] for r in self.records), 1)

    @property
    def total_cost(self) -> float:
        return round(sum(r["cost"] for r in self.records), 2)
