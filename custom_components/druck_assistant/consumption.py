"""Home Assistant independent split of a print's filament over the spools used.

A print can use several slots (multi color) and a slot can change during the print
(a spool runs empty and the AMS continues with another spool of the same filament).
The printer reports one total weight, optionally the planned grams per slot, the
remaining percent per slot and when the active slot changed; this module turns that
into grams per slot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SlotInfo:
    """What is known about one slot taking part in a print."""

    key: str
    material: str = ""
    # Grams left on the assigned spool when the print started (None: unknown).
    capacity_g: float | None = None
    # Grams the AMS remaining percent dropped during the print (None: not measurable).
    measured_g: float | None = None


@dataclass
class Segment:
    """A stretch of the print during which one slot was active."""

    slot: str
    start: float  # print progress in percent when the slot became active


@dataclass
class Usage:
    slot: str
    grams: float


def measured_grams(
    remain_start: Any, remain_end: Any, initial_g: float | None
) -> float | None:
    """Grams a slot lost according to the AMS remaining percent (None if unusable)."""
    if not initial_g or initial_g <= 0:
        return None
    for value in (remain_start, remain_end):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
            return None
    return max(0.0, (remain_start - remain_end) * initial_g / 100)


def _shares(segments: list[Segment], end: float) -> dict[str, float]:
    """Fraction of the print each slot was active (by progress)."""
    shares: dict[str, float] = {}
    for i, seg in enumerate(segments):
        stop = segments[i + 1].start if i + 1 < len(segments) else end
        length = max(0.0, min(stop, end) - min(seg.start, end))
        shares[seg.slot] = shares.get(seg.slot, 0.0) + length
    total = sum(shares.values())
    if total <= 0:
        # No progress information: every slot that was active counts the same.
        return {slot: 1 / len(shares) for slot in shares} if shares else {}
    return {slot: value / total for slot, value in shares.items()}


def _split(weight: float, members: list[SlotInfo], shares: dict[str, float]) -> dict[str, float]:
    """Distribute weight over the slots that served one filament, in order of use."""
    if len(members) == 1:
        return {members[0].key: weight}
    measured = [m.measured_g for m in members]
    if all(v is not None for v in measured) and sum(measured) > 0:
        total = sum(measured)
        return {m.key: weight * m.measured_g / total for m in members}
    if all(m.capacity_g is not None for m in members):
        # A spool is used up before the next one takes over: fill them in order.
        result: dict[str, float] = {}
        left = weight
        for m in members[:-1]:
            take = min(left, max(m.capacity_g, 0.0))
            result[m.key] = take
            left -= take
        result[members[-1].key] = left
        return result
    share = [shares.get(m.key, 0.0) for m in members]
    if sum(share) <= 0:
        share = [1.0] * len(members)
    total = sum(share)
    return {m.key: weight * s / total for m, s in zip(members, share, strict=True)}


def split_usage(
    total_g: float,
    *,
    finished: bool,
    progress: float | None,
    segments: list[Segment],
    slots: dict[str, SlotInfo],
    plan: dict[str, float] | None = None,
) -> list[Usage]:
    """Grams used per slot.

    total_g is the weight of the whole print as sliced; a print that did not finish
    counts only for the progress it reached. plan holds the sliced grams per slot
    when the printer knows them (the slot that was planned stands for its filament).
    Slots that were active without being planned continue the filament of the planned
    slot with the same material (a refill after a spool ran empty).
    """
    if total_g <= 0 or not segments:
        return []
    fraction = 1.0 if finished or progress is None else max(0.0, min(progress, 100.0)) / 100
    end = 100.0 if finished or progress is None else max(0.0, min(progress, 100.0))
    shares = _shares(segments, end)
    order: list[str] = []
    for seg in segments:
        if seg.slot not in order:
            order.append(seg.slot)

    def info(key: str) -> SlotInfo:
        return slots.get(key) or SlotInfo(key)

    pools: list[tuple[float, list[SlotInfo]]] = []
    if plan:
        planned = {k: g for k, g in plan.items() if g > 0}
        if planned:
            used_by: dict[str, list[SlotInfo]] = {k: [info(k)] for k in planned}
            for key in order:
                if key in planned:
                    continue
                material = info(key).material.lower()
                owner = next(
                    (p for p in planned if material and info(p).material.lower() == material),
                    None,
                )
                if owner is not None:
                    used_by[owner].append(info(key))
            for owner, grams in planned.items():
                members = used_by[owner]
                members.sort(key=lambda m: order.index(m.key) if m.key in order else len(order))
                pools.append((grams * fraction, members))
    if not pools:
        pools = [(total_g * fraction, [info(k) for k in order])]

    totals: dict[str, float] = {}
    for weight, members in pools:
        for key, grams in _split(weight, members, shares).items():
            totals[key] = totals.get(key, 0.0) + grams
    usages = [Usage(key, round(grams, 1)) for key, grams in totals.items() if grams > 0]
    return usages


@dataclass
class UsageTracker:
    """Collects the slot changes of a running print."""

    segments: list[Segment] = field(default_factory=list)

    def note(self, slot: str | None, progress: float | None) -> None:
        if not slot:
            return
        if self.segments and self.segments[-1].slot == slot:
            return
        self.segments.append(Segment(slot, float(progress or 0.0)))
