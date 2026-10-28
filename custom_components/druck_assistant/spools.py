"""Home Assistant independent filament spool inventory."""

from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass
from typing import Any

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


MAX_COLOR_DISTANCE = 90  # RGB distance (0-441) up to which two colors count as the same
# Catalog spools carry the exact manufacturer color, so within one product line
# (Bambu PLA Matte vs. Bambu PLA Matte) only a near-identical color is the same spool.
MAX_SAME_PRODUCT_DISTANCE = 20


def _rgb(color: str) -> tuple[int, int, int] | None:
    if not HEX_COLOR.match(color or ""):
        return None
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def color_distance(a: str, b: str) -> float | None:
    """Euclidean RGB distance of two #rrggbb[aa] colors, None if either is missing."""
    ca, cb = _rgb(a), _rgb(b)
    if ca is None or cb is None:
        return None
    return sum((x - y) ** 2 for x, y in zip(ca, cb)) ** 0.5


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
    archived: bool = False

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


def _product_line(stock_name: str, tray_name: str) -> str:
    """Compare two "<brand> <material> <variant>" names: "same", "other" or "".

    "Bambu PLA Matte" and "Bambu PLA Basic" share brand and material but are
    "other" variants, so a close color must not make one stand in for the other.
    Names that do not follow this shape (like "Black PETG") give "".
    """
    stock = re.sub(r"\s+#\d+$", "", stock_name.strip()).lower().split()
    tray = re.sub(r"\s+#\d+$", "", tray_name.strip()).lower().split()
    if len(stock) < 3 or len(tray) < 3 or stock[:2] != tray[:2]:
        return ""
    return "same" if stock[2:] == tray[2:] else "other"


class SpoolStore:
    """Spool inventory and slot assignments (slot key -> spool id)."""

    def __init__(
        self,
        spools: list[dict[str, Any]] | None = None,
        assignments: dict[str, str] | None = None,
        dismissed_rfids: list[str] | None = None,
    ) -> None:
        self.spools: dict[str, Spool] = {}
        for item in spools or []:
            fields = {k: v for k, v in item.items() if k in Spool.__dataclass_fields__}
            self.spools[fields["id"]] = Spool(**fields)
        self.assignments: dict[str, str] = {
            k: v for k, v in (assignments or {}).items() if v in self.spools
        }
        # Tags the user cleared from a slot by hand: not auto-assigned again.
        self.dismissed_rfids: set[str] = set(dismissed_rfids or [])

    def to_dict(self) -> dict[str, Any]:
        return {
            "spools": [asdict(s) for s in self.spools.values()],
            "assignments": dict(self.assignments),
            "dismissed_rfids": sorted(self.dismissed_rfids),
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
            archived=existing.archived if existing else False,
        )
        self.spools[spool.id] = spool
        if spool.rfid:
            self._move_tag(spool.rfid, spool)
        return spool

    def add_spools(self, data: dict[str, Any], quantity: int = 1) -> list[Spool]:
        """Add several identical spools at once (e.g. a 4-pack); numbered if more than one."""
        if not 1 <= quantity <= 50:
            raise SpoolError("quantity must be between 1 and 50")
        if quantity == 1:
            return [self.save_spool(data)]
        base = {k: v for k, v in data.items() if k != "id"}
        name = str(base.get("name", "")).strip()
        return [
            self.save_spool({**base, "name": f"{name} #{i}" if name else name})
            for i in range(1, quantity + 1)
        ]

    def find_stock(self, attrs: dict[str, Any]) -> Spool | None:
        """Best matching spool that is in stock: not in a slot, untagged, same material.

        The color must be close to the tray color (or unknown on the stock spool),
        and a spool of another variant of the same product line (PLA Matte for
        PLA Basic) never counts. Within the same product line the color must be
        nearly identical (a pink PLA Matte is not the stock's latte brown one).
        Among matches the closest color wins, then the fullest spool.
        """
        material = str(attrs.get("type") or "").strip().lower()
        color = str(attrs.get("color") or "")
        tray_name = str(attrs.get("name") or "")
        assigned = set(self.assignments.values())
        best: tuple[float, float] | None = None
        found: Spool | None = None
        for spool in self.spools.values():
            if (
                spool.archived
                or spool.rfid
                or spool.id in assigned
                or spool.material.strip().lower() != material
            ):
                continue
            line = _product_line(spool.name, tray_name)
            if line == "other":
                continue
            limit = MAX_SAME_PRODUCT_DISTANCE if line == "same" else MAX_COLOR_DISTANCE
            distance = color_distance(spool.color, color)
            if distance is None:
                # No usable color on one side: a weaker match than any close color.
                distance = limit + 1
            elif distance > limit:
                continue
            rank = (distance, -spool.remaining_g)
            if best is None or rank < best:
                best, found = rank, spool
        return found

    def find_by_rfid(self, rfid: str) -> Spool | None:
        rfid = valid_rfid(rfid)
        return next((s for s in self.spools.values() if rfid and s.rfid == rfid), None)

    def import_slot(
        self, slot: str, attrs: dict[str, Any], *, include_untagged: bool
    ) -> tuple[str, Spool | None]:
        """Create or link a spool for an AMS slot from ha-bambulab tray attributes.

        Returns (action, spool) with action one of "created", "assigned",
        "adopted", "synced", "skipped". New spools are matched against the stock first
        (see find_stock), so a pre-entered 4-pack is used up instead of duplicated. Spools with an RFID tag are matched by tag, so the
        same spool is recognized when it moves to another slot. Untagged spools
        are only imported when include_untagged is set (manual import).
        """
        rfid = valid_rfid(attrs.get("tray_uuid")) or valid_rfid(attrs.get("tag_uid"))
        material = str(attrs.get("type") or "").strip()
        if attrs.get("empty") or not material:
            return "skipped", None
        current = self.spool_for_slot(slot)

        if rfid and rfid in self.dismissed_rfids:
            if not include_untagged:  # manual import overrides an earlier dismissal
                return "skipped", None
            self.dismissed_rfids.discard(rfid)

        if rfid:
            known = self.find_by_rfid(rfid)
            if known is not None:
                if current is not None and current.id == known.id:
                    return ("synced" if self._sync_remaining(known, attrs) else "skipped"), known
                if known.archived:
                    # An archived spool is still in the AMS (e.g. just ran empty).
                    # Never bring it back automatically: restore it from the archive.
                    return "skipped", known
                self.assign(slot, known.id)
                return "assigned", known
            if current is not None and not current.rfid:
                # The user already put a spool in this slot by hand: tag it.
                current.rfid = rfid
                return "adopted", current
        elif current is not None or not include_untagged:
            return "skipped", current

        stock = self.find_stock(attrs)
        if stock is not None:
            # A spool bought earlier and added by hand: this is it.
            stock.rfid = rfid
            self.assign(slot, stock.id)
            return ("adopted" if rfid else "assigned"), stock

        spool = self.save_spool(spool_data_from_tray(attrs, rfid))
        self.assign(slot, spool.id)
        return "created", spool

    @staticmethod
    def _sync_remaining(spool: Spool, attrs: dict[str, Any]) -> bool:
        """Take the AMS remaining amount for a spool that still counts as full.

        A new spool is first reported with an unknown remaining amount (-1), so it
        is created as full; the real value follows a little later. Only a spool
        that is still exactly full is corrected, never one tracked by prints.
        """
        remain = attrs.get("remain")
        if (
            not attrs.get("remain_enabled", True)
            or not isinstance(remain, (int, float))
            or not 0 <= remain < 100
            or spool.remaining_g != spool.initial_weight_g
        ):
            return False
        spool.remaining_g = round(spool.initial_weight_g * remain / 100, 1)
        return True

    def delete_spool(self, spool_id: str) -> None:
        if self.spools.pop(spool_id, None) is None:
            raise SpoolError("unknown spool")
        self.assignments = {k: v for k, v in self.assignments.items() if v != spool_id}

    def archive(self, spool_id: str, archived: bool = True) -> Spool:
        """Move a spool to the archive (or back). Archived spools leave their slot."""
        spool = self.spools.get(spool_id)
        if spool is None:
            raise SpoolError("unknown spool")
        spool.archived = archived
        if archived:
            self.assignments = {k: v for k, v in self.assignments.items() if v != spool_id}
        return spool

    def assign(self, slot: str, spool_id: str | None, tag: str = "") -> None:
        """Assign a spool to a slot (a spool sits in one slot only); None clears it.

        tag is the RFID tag the tray currently reports. When given, a manual
        correction wins over the automatic match: the tag moves to the chosen
        spool (so the automatic import keeps agreeing with you), and clearing the
        slot makes the automatic import leave this tag alone.
        """
        tag = valid_rfid(tag)
        if spool_id is None:
            self.assignments.pop(slot, None)
            if tag:
                self.dismissed_rfids.add(tag)
            return
        if spool_id not in self.spools:
            raise SpoolError("unknown spool")
        spool = self.spools[spool_id]
        if spool.archived:
            raise SpoolError("spool is archived")
        self.assignments = {k: v for k, v in self.assignments.items() if v != spool_id}
        self.assignments[slot] = spool_id
        if tag:
            self._move_tag(tag, spool)
            self.dismissed_rfids.discard(tag)

    def _move_tag(self, tag: str, target: Spool) -> None:
        """Make target the only spool carrying tag."""
        for other in self.spools.values():
            if other.id != target.id and other.rfid == tag:
                other.rfid = ""
        target.rfid = tag

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
            if s.id in assigned and not s.archived and s.remaining_percent <= threshold_percent
        ]
