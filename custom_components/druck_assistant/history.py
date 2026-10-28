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
from .consumption import UsageTracker


_MINUTES_PER_UNIT = {"s": 1 / 60, "min": 1.0, "h": 60.0, "d": 1440.0}


def to_minutes(value: float | None, unit: str | None) -> float | None:
    """Convert a duration sensor value to minutes (the unit is what the entity displays)."""
    if value is None:
        return None
    return value * _MINUTES_PER_UNIT.get(unit or "min", 1.0)


def calculate_cost(weight_g: float | None, price_per_kg: float) -> float:
    """Return the filament cost for a print."""
    if not weight_g or weight_g < 0:
        return 0.0
    return round(weight_g / 1000 * price_per_kg, 2)


def calculate_energy_cost(energy_kwh: float | None, price_per_kwh: float) -> float:
    """Return the electricity cost for a print."""
    if not energy_kwh or energy_kwh < 0:
        return 0.0
    return round(energy_kwh * price_per_kwh, 2)


def parse_prices(text: str | None) -> dict[str, float]:
    """Parse "PLA=20" style lines (separated by newline or ';') into a dict.

    Keys are upper-cased. Raises ValueError on a malformed line.
    """
    prices: dict[str, float] = {}
    for part in (text or "").replace(";", "\n").splitlines():
        part = part.strip()
        if not part:
            continue
        name, sep, value = part.partition("=")
        name = name.strip().upper()
        if not sep or not name:
            raise ValueError(part)
        price = float(value.strip().replace(",", "."))
        if price < 0:
            raise ValueError(part)
        prices[name] = price
    return prices


def price_for(
    material: str | None, prices: dict[str, float], default: float
) -> float:
    """Price per kg for a filament type, falling back to the default."""
    if material:
        key = material.strip().upper()
        if key in prices:
            return prices[key]
        # "PLA-CF" or "PLA Basic" -> try the longest matching prefix.
        for name in sorted(prices, key=len, reverse=True):
            if key.startswith(name):
                return prices[name]
    return default


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
    price_per_kg: float = 0.0
    spool_id: str | None = None
    spool_name: str | None = None
    filament_cost: float = 0.0
    energy_kwh: float = 0.0
    energy_cost: float = 0.0
    material: str | None = None
    color: str | None = None
    filament: dict[str, float] = field(default_factory=dict)
    # Filament per spool when the print used more than one (or the weight was split):
    # [{"spool_id", "spool_name", "weight_g", "price_per_kg", "cost", "material", "color"}]
    usages: list[dict[str, Any]] = field(default_factory=list)
    # The weight of the whole print as sliced; weight_g is what was actually counted.
    planned_g: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PrintSession:
    """The print currently in progress."""

    started: datetime
    name: str | None = None
    material: str | None = None
    color: str | None = None
    energy_start_kwh: float | None = None
    power_w: float | None = None
    power_ts: datetime | None = None
    energy_acc_kwh: float = 0.0
    slot_key: str | None = None
    spool_id: str | None = None
    spool_name: str | None = None
    # Slot changes of the print and the state of every slot at its start (see consumption.py).
    usage: UsageTracker = field(default_factory=UsageTracker)
    start_slots: dict[str, dict[str, Any]] = field(default_factory=dict)
    progress: float | None = None
    plan: dict[str, float] = field(default_factory=dict)
    warned: bool = False

    def add_power(self, now: datetime, watts: float | None) -> None:
        """Integrate the previous power reading up to now and store the new one."""
        if self.power_w is not None and self.power_ts is not None:
            hours = (now - self.power_ts).total_seconds() / 3600
            self.energy_acc_kwh += self.power_w * hours / 1000
        self.power_w = watts
        self.power_ts = now

    def estimate_energy_kwh(self, now: datetime, energy_now_kwh: float | None) -> float:
        """Energy used so far without changing the session (for live display)."""
        if (
            self.energy_start_kwh is not None
            and energy_now_kwh is not None
            and energy_now_kwh >= self.energy_start_kwh
        ):
            return energy_now_kwh - self.energy_start_kwh
        pending = 0.0
        if self.power_w is not None and self.power_ts is not None:
            pending = self.power_w * (now - self.power_ts).total_seconds() / 3600 / 1000
        return self.energy_acc_kwh + pending

    def energy_kwh(self, now: datetime, energy_end_kwh: float | None) -> float:
        """Energy used so far: meter delta if available, else integrated power."""
        if (
            self.energy_start_kwh is not None
            and energy_end_kwh is not None
            and energy_end_kwh >= self.energy_start_kwh
        ):
            return energy_end_kwh - self.energy_start_kwh
        self.add_power(now, self.power_w)
        return self.energy_acc_kwh


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
        energy_end_kwh: float | None = None,
        price_per_kwh: float = 0.0,
        usages: list[dict[str, Any]] | None = None,
        planned_g: float | None = None,
    ) -> PrintRecord | None:
        """Close the session and store the record."""
        session, self.session = self.session, None
        if session is None:
            return None
        weight = float(weight_g or 0)
        filament_cost = calculate_cost(weight, price_per_kg)
        usages = [dict(u) for u in usages or []]
        if usages:
            # Several spools (or a part of a failed print): every spool is charged on its own.
            for usage in usages:
                usage["cost"] = calculate_cost(usage["weight_g"], usage["price_per_kg"])
            weight = round(sum(u["weight_g"] for u in usages), 1)
            filament_cost = round(sum(u["cost"] for u in usages), 2)
            price_per_kg = round(filament_cost / weight * 1000, 2) if weight else price_per_kg
        energy = round(session.energy_kwh(now, energy_end_kwh), 3)
        energy_cost = calculate_energy_cost(energy, price_per_kwh)
        record = PrintRecord(
            name=name or session.name or "unknown",
            result=result,
            started=session.started.isoformat(),
            finished=now.isoformat(),
            duration_min=round((now - session.started).total_seconds() / 60, 1),
            weight_g=weight,
            cost=round(filament_cost + energy_cost, 2),
            price_per_kg=price_per_kg,
            spool_id=usages[0]["spool_id"] if usages else session.spool_id,
            spool_name=usages[0]["spool_name"] if usages else session.spool_name,
            filament_cost=filament_cost,
            energy_kwh=energy,
            energy_cost=energy_cost,
            material=session.material,
            color=session.color,
            filament=dict(filament or {}),
            usages=usages if len(usages) > 1 else [],
            planned_g=planned_g,
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

    def find(self, started: str) -> dict[str, Any] | None:
        return next((r for r in self.records if r.get("started") == started), None)

    def rebook(
        self,
        started: str,
        spool_id: str | None,
        spool_name: str | None,
        price_per_kg: float,
        material: str | None = None,
        color: str | None = None,
    ) -> tuple[str | None, float]:
        """Charge a recorded print to another spool.

        Returns (previous spool id, grams) so the caller can move the stock. Prints
        that used several spools cannot be rebooked as a whole.
        """
        record = self.find(started)
        if record is None:
            raise KeyError(started)
        if record.get("usages"):
            raise ValueError("print used several spools")
        previous = record.get("spool_id")
        grams = float(record.get("weight_g") or 0)
        filament_cost = calculate_cost(grams, price_per_kg)
        record.update(
            spool_id=spool_id,
            spool_name=spool_name,
            price_per_kg=price_per_kg,
            filament_cost=filament_cost,
            cost=round(filament_cost + float(record.get("energy_cost") or 0), 2),
        )
        if material:
            record["material"] = material
        if color:
            record["color"] = color
        return previous, grams

    @property
    def total_weight_g(self) -> float:
        return round(sum(r["weight_g"] for r in self.records), 1)

    @property
    def total_energy_kwh(self) -> float:
        return round(sum(r.get("energy_kwh", 0) for r in self.records), 3)

    @property
    def total_energy_cost(self) -> float:
        return round(sum(r.get("energy_cost", 0) for r in self.records), 2)

    @property
    def total_filament_cost(self) -> float:
        # Records from before the split only have the total (which then was filament only).
        return round(
            sum(r.get("filament_cost", r["cost"] - r.get("energy_cost", 0)) for r in self.records),
            2,
        )

    @property
    def total_cost(self) -> float:
        return round(sum(r["cost"] for r in self.records), 2)
