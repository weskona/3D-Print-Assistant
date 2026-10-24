"""Home Assistant independent filament spool inventory."""

from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass
from typing import Any

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


class SpoolError(ValueError):
    """Raised for invalid spool data or unknown spools."""


def _number(value: Any, field: str, *, optional: bool = False) -> float | None:
    if value in (None, ""):
        if optional:
            return None
        raise SpoolError(f"{field} is required")
    try:
        number = float(value)
    except (TypeError, ValueError) as err:
        raise SpoolError(f"{field} must be a number") from err
    if number < 0:
        raise SpoolError(f"{field} must not be negative")
    return number


@dataclass
class Spool:
    """A filament spool."""

    id: str
    name: str
    material: str
    brand: str = ""
    color: str = ""
    price_per_kg: float | None = None
    initial_weight_g: float = 1000.0
    remaining_g: float = 1000.0
    notes: str = ""

    @property
    def remaining_percent(self) -> float:
        if not self.initial_weight_g:
            return 0.0
        return round(self.remaining_g / self.initial_weight_g * 100, 1)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["remaining_percent"] = self.remaining_percent
        return data


class SpoolStore:
    """Spool inventory and slot assignments (slot key -> spool id)."""

    def __init__(
        self,
        spools: list[dict[str, Any]] | None = None,
        assignments: dict[str, str] | None = None,
    ) -> None:
        self.spools: dict[str, Spool] = {}
        for item in spools or []:
            fields = {k: v for k, v in item.items() if k in Spool.__dataclass_fields__}
            self.spools[fields["id"]] = Spool(**fields)
        self.assignments: dict[str, str] = {
            k: v for k, v in (assignments or {}).items() if v in self.spools
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "spools": [asdict(s) for s in self.spools.values()],
            "assignments": dict(self.assignments),
        }

    def save_spool(self, data: dict[str, Any]) -> Spool:
        """Create a spool, or update the spool with data["id"]."""
        name = str(data.get("name", "")).strip()
        material = str(data.get("material", "")).strip()
        if not name:
            raise SpoolError("name is required")
        if not material:
            raise SpoolError("material is required")
        color = str(data.get("color") or "").strip()
        if color and not HEX_COLOR.match(color):
            raise SpoolError("color must be a hex value like #ff0000")
        price = _number(data.get("price_per_kg"), "price_per_kg", optional=True)
        initial = _number(data.get("initial_weight_g", 1000), "initial_weight_g")
        remaining = _number(data.get("remaining_g", initial), "remaining_g")
        if not initial:
            raise SpoolError("initial_weight_g must be greater than 0")
        remaining = min(remaining, initial) if data.get("id") is None else remaining

        spool_id = data.get("id")
        if spool_id is not None and spool_id not in self.spools:
            raise SpoolError("unknown spool")
        spool = Spool(
            id=spool_id or uuid.uuid4().hex[:8],
            name=name,
            material=material,
            brand=str(data.get("brand") or "").strip(),
            color=color,
            price_per_kg=price,
            initial_weight_g=initial,
            remaining_g=remaining,
            notes=str(data.get("notes") or "").strip(),
        )
        self.spools[spool.id] = spool
        return spool

    def delete_spool(self, spool_id: str) -> None:
        if self.spools.pop(spool_id, None) is None:
            raise SpoolError("unknown spool")
        self.assignments = {k: v for k, v in self.assignments.items() if v != spool_id}

    def assign(self, slot: str, spool_id: str | None) -> None:
        """Assign a spool to a slot (a spool sits in one slot only); None clears it."""
        if spool_id is None:
            self.assignments.pop(slot, None)
            return
        if spool_id not in self.spools:
            raise SpoolError("unknown spool")
        self.assignments = {k: v for k, v in self.assignments.items() if v != spool_id}
        self.assignments[slot] = spool_id

    def spool_for_slot(self, slot: str | None) -> Spool | None:
        spool_id = self.assignments.get(slot) if slot else None
        return self.spools.get(spool_id) if spool_id else None

    def consume(self, spool_id: str | None, grams: float | None) -> Spool | None:
        """Deduct used filament, never going below zero."""
        spool = self.spools.get(spool_id) if spool_id else None
        if spool is None or not grams or grams <= 0:
            return spool
        spool.remaining_g = round(max(spool.remaining_g - grams, 0.0), 1)
        return spool

    def low_spools(self, threshold_percent: float) -> list[Spool]:
        """Assigned spools at or below the threshold."""
        assigned = set(self.assignments.values())
        return [
            s
            for s in self.spools.values()
            if s.id in assigned and s.remaining_percent <= threshold_percent
        ]
