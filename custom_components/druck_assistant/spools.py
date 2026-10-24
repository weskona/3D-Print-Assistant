"""Home Assistant independent filament spool inventory."""

from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass
from typing import Any

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


def valid_rfid(value: Any) -> str:
    """Return a usable spool tag id, or "" (Bambu reports all zeros for non-RFID spools)."""
    text = str(value or "").strip()
    return "" if not text or set(text) <= {"0"} else text


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
    rfid: str = ""

    @property
    def remaining_percent(self) -> float:
        if not self.initial_weight_g:
            return 0.0
        return round(self.remaining_g / self.initial_weight_g * 100, 1)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["remaining_percent"] = self.remaining_percent
        return data


def spool_data_from_tray(attrs: dict[str, Any], rfid: str) -> dict[str, Any]:
    """Spool fields derived from ha-bambulab tray attributes."""
    material = str(attrs.get("type") or "").strip()
    try:
        initial = float(attrs.get("tray_weight") or 0) or 1000.0
    except (TypeError, ValueError):
        initial = 1000.0
    remain = attrs.get("remain")
    if attrs.get("remain_enabled", True) and isinstance(remain, (int, float)) and 0 <= remain <= 100:
        remaining = round(initial * remain / 100, 1)
    else:
        remaining = initial
    color = str(attrs.get("color") or "")
    return {
        "name": str(attrs.get("name") or material).strip() or material,
        "material": material,
        "brand": "Bambu Lab" if rfid else "",
        "color": color if HEX_COLOR.match(color) else "",
        "initial_weight_g": initial,
        "remaining_g": remaining,
        "rfid": rfid,
    }


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
        existing = self.spools.get(spool_id) if spool_id else None
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
            rfid=valid_rfid(data["rfid"]) if "rfid" in data
            else (existing.rfid if existing else ""),
        )
        self.spools[spool.id] = spool
        return spool

    def find_by_rfid(self, rfid: str) -> Spool | None:
        rfid = valid_rfid(rfid)
        return next((s for s in self.spools.values() if rfid and s.rfid == rfid), None)

    def import_slot(
        self, slot: str, attrs: dict[str, Any], *, include_untagged: bool
    ) -> tuple[str, Spool | None]:
        """Create or link a spool for an AMS slot from ha-bambulab tray attributes.

        Returns (action, spool) with action one of "created", "assigned",
        "adopted", "skipped". Spools with an RFID tag are matched by tag, so the
        same spool is recognized when it moves to another slot. Untagged spools
        are only imported when include_untagged is set (manual import).
        """
        rfid = valid_rfid(attrs.get("tray_uuid")) or valid_rfid(attrs.get("tag_uid"))
        material = str(attrs.get("type") or "").strip()
        if attrs.get("empty") or not material:
            return "skipped", None
        current = self.spool_for_slot(slot)

        if rfid:
            known = self.find_by_rfid(rfid)
            if known is not None:
                if current is not None and current.id == known.id:
                    return "skipped", known
                self.assign(slot, known.id)
                return "assigned", known
            if current is not None and not current.rfid:
                # The user already put a spool in this slot by hand: tag it.
                current.rfid = rfid
                return "adopted", current
        elif current is not None or not include_untagged:
            return "skipped", current

        spool = self.save_spool(spool_data_from_tray(attrs, rfid))
        self.assign(slot, spool.id)
        return "created", spool

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
