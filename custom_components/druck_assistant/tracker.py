"""Track a ha-bambulab printer and keep print history."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    BAMBU_DOMAIN,
    CONF_AUTO_ARCHIVE,
    CONF_AUTO_IMPORT,
    CONF_ENERGY_ENTITY,
    CONF_FILAMENT_PRICES,
    CONF_MIN_STOCK,
    CONF_NOTIFY_FILAMENT_LOW,
    CONF_POWER_ENTITY,
    CONF_PRICE_ENTITY,
    CONF_PRICE_PER_KG,
    CONF_PRICE_PER_KWH,
    CONF_SERIAL,
    DEFAULT_FILAMENT_LOW,
    DEFAULT_PRICE_PER_KG,
    DEFAULT_PRICE_PER_KWH,
    DOMAIN,
    EVENT_FILAMENT_LOW,
    EVENT_PRINT_FAILED,
    EVENT_PRINT_FINISHED,
    EVENT_PRINT_STARTED,
    EVENT_SPOOL_EMPTY,
    EVENT_SPOOL_IMPORTED,
    EVENT_SPOOL_INSUFFICIENT,
    EVENT_STOCK_LOW,
    STATUS_FAILED,
    STATUS_FINISH,
    STORAGE_VERSION,
)
from .consumption import Segment, SlotInfo, measured_grams, shortages, split_usage
from .history import PrintHistory, parse_prices, price_for, to_minutes
from .spools import valid_rfid

UNAVAILABLE = ("unknown", "unavailable", None)


_LOGGER = logging.getLogger(__name__)

# Below this progress the printer's start time may still belong to the previous job.
MIN_PROGRESS_FOR_START_TIME = 3.0

class PrintTracker:
    """Listens to ha-bambulab entities and records prints."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.serial: str = entry.data[CONF_SERIAL]
        self.history = PrintHistory()
        self.signal = f"{DOMAIN}_update_{entry.entry_id}"
        self._store: Store = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}"
        )
        self._low_notified: set[str] = set()
        self.filament = hass.data[DOMAIN]["filament"]

    @property
    def price_per_kg(self) -> float:
        return self.entry.options.get(CONF_PRICE_PER_KG, DEFAULT_PRICE_PER_KG)

    def price_for_material(self, material: str | None) -> float:
        """Price per kg for a filament type (option 'PLA=20' lines, else default)."""
        try:
            prices = parse_prices(self.entry.options.get(CONF_FILAMENT_PRICES))
        except ValueError:
            prices = {}
        return price_for(material, prices, self.price_per_kg)

    def tray_price_per_kg(self) -> float:
        """Price per kg of the active tray: its assigned spool if that has a price, else the material price."""
        tray = self.current_tray
        spool = self.filament.store.spool_for_slot(self.active_slot_key())
        if spool is not None and spool.price_per_kg is not None:
            return spool.price_per_kg
        return self.price_for_material(tray.attributes.get("type") if tray else None)

    def current_print(self) -> dict[str, Any] | None:
        """The print in progress for the panel, from ha-bambulab entities and our session."""
        status = self._value("print_status")
        session = self.history.session
        if status not in ("running", "pause", "prepare") and session is None:
            return None
        now = dt_util.utcnow()
        tray = self.current_tray
        spool = (
            self.filament.store.spools.get(session.spool_id)
            if session and session.spool_id
            else None
        )
        material = (
            spool.material
            if spool
            else (session.material if session and session.material else None)
            or (tray.attributes.get("type") if tray else None)
        )
        price = (
            spool.price_per_kg
            if spool is not None and spool.price_per_kg is not None
            else self.price_for_material(material)
        )
        weight = self._float("print_weight")
        energy = (
            session.estimate_energy_kwh(now, self._external_float(CONF_ENERGY_ENTITY))
            if session
            else None
        )
        filament_cost = round(weight / 1000 * price, 2) if weight and price else None
        energy_cost = round(energy * self.price_per_kwh, 2) if energy else None
        total = (
            round((filament_cost or 0) + (energy_cost or 0), 2)
            if filament_cost is not None or energy_cost is not None
            else None
        )
        return {
            "status": status,
            "name": self._value("subtask_name") or (session.name if session else None),
            "progress": self._float("print_progress"),
            "started": self._value("start_time")
            or (session.started.isoformat() if session else None),
            "remaining_min": self._minutes("remaining_time"),
            "end": self._value("end_time"),
            "layer": self._float("current_layer"),
            "total_layers": self._float("total_layers"),
            "weight_g": weight,
            "nozzle_temp": self._float("nozzle_temp"),
            "bed_temp": self._float("bed_temp"),
            "spool": spool.name if spool else None,
            "material": material,
            "color": (spool.color if spool else None)
            or (session.color if session else None)
            or (tray.attributes.get("color") if tray else None),
            "price_per_kg": price,
            "shortages": self.shortages_now(),
            "filament_cost": filament_cost,
            "energy_kwh": round(energy, 3) if energy is not None else None,
            "energy_cost": energy_cost,
            "total_cost": total,
        }

    def panel_data(self) -> dict[str, Any]:
        """Everything the panel needs for this printer."""
        session = self.history.session
        tray = self.current_tray
        h = self.history
        return {
            "entry_id": self.entry.entry_id,
            "title": self.entry.title,
            "serial": self.serial,
            "currency": "EUR",
            "price_per_kwh": self.price_per_kwh,
            "totals": {
                "prints": h.total_prints,
                "successful": h.successful_prints,
                "weight_g": h.total_weight_g,
                "cost": h.total_cost,
                "energy_kwh": h.total_energy_kwh,
                "energy_cost": h.total_energy_cost,
                "filament_cost": h.total_filament_cost,
            },
            "current_print": self.current_print(),
            # The panel reads this entity's state live from Home Assistant.
            "stage_entity": self.entity_id("stage"),
            "camera_entity": self.entity_id("camera", "camera"),
            "cover_entity": self.entity_id("cover_image", "image"),
            "session": None
            if session is None
            else {
                "name": session.name,
                "started": session.started.isoformat(),
                "material": session.material,
                "color": session.color,
            },
            "filament": None
            if tray is None
            else {
                "type": tray.attributes.get("type"),
                "name": tray.attributes.get("name"),
                "color": tray.attributes.get("color"),
                "remain": tray.attributes.get("remain"),
                "price_per_kg": self.tray_price_per_kg(),
            },
            "history": h.records[::-1],
            "slots": self.slots(),
        }

    def slot_entities(self) -> dict[str, str]:
        """Slot key -> entity id of the ha-bambulab tray sensors of this printer."""
        prefix = f"_{self.serial}_"
        found = {}
        for entry in er.async_get(self.hass).entities.values():
            uid = entry.unique_id
            if (
                entry.platform == BAMBU_DOMAIN
                and entry.domain == "sensor"
                and prefix in uid
                and (re.search(r"_AMS_.*_tray_\d$", uid) or "_ExternalSpool" in uid)
            ):
                found[f"{self.serial}:{uid.split(prefix, 1)[1]}"] = entry.entity_id
        return found

    def slots(self) -> list[dict[str, Any]]:
        """AMS and external spool slots of this printer, from ha-bambulab tray sensors."""
        slots = []
        for key, entity_id in self.slot_entities().items():
            state = self.hass.states.get(entity_id)
            if state is None or "active" not in state.attributes:
                continue
            attrs = state.attributes
            spool = self.filament.store.spool_for_slot(key)
            slots.append(
                {
                    "key": key,
                    "label": attrs.get("friendly_name") or entity_id,
                    "active": bool(attrs.get("active")),
                    "type": attrs.get("type"),
                    "color": attrs.get("color"),
                    "remain": attrs.get("remain"),
                    "tagged": bool(
                        valid_rfid(attrs.get("tray_uuid")) or valid_rfid(attrs.get("tag_uid"))
                    ),
                    "spool_id": spool.id if spool else None,
                    "replacement": self._replacement(spool),
                }
            )
        return sorted(slots, key=lambda s: s["key"])

    def _replacement(self, spool) -> dict[str, Any] | None:
        """The stock spool to insert when this one runs out (only for a low spool)."""
        if spool is None or spool.remaining_percent > self.low_threshold:
            return None
        other = self.filament.store.replacement_for(spool)
        if other is None:
            return None
        return {"id": other.id, "name": other.name, "remaining_g": other.remaining_g}

    def import_from_ams(self, *, include_untagged: bool) -> dict[str, list[dict[str, Any]]]:
        """Create or link spools for the current AMS contents."""
        result: dict[str, list[dict[str, Any]]] = {
            "created": [], "assigned": [], "adopted": [], "synced": [],
        }
        for key, entity_id in self.slot_entities().items():
            state = self.hass.states.get(entity_id)
            if state is None or "active" not in state.attributes:
                continue
            action, spool = self.filament.store.import_slot(
                key, dict(state.attributes), include_untagged=include_untagged
            )
            if action in result and spool is not None:
                result[action].append({"slot": key, "spool": self.filament.store.spool_dict(spool)})
                self.hass.bus.async_fire(
                    EVENT_SPOOL_IMPORTED,
                    {"serial": self.serial, "action": action, "slot": key, "spool": spool.name},
                )
        if any(result.values()):
            self.filament.changed()
        return result

    def low_spools(self):
        """Spools in this printer's slots that are at or below the low threshold."""
        store = self.filament.store
        slot_keys = {s["key"] for s in self.slots()}
        return [
            s
            for s in store.low_spools(self.low_threshold)
            if any(store.assignments.get(k) == s.id for k in slot_keys)
        ]

    def slot_tag(self, slot_key: str) -> str:
        """RFID tag the tray in this slot currently reports ("" if none)."""
        entity_id = self.slot_entities().get(slot_key)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None:
            return ""
        attrs = state.attributes
        return valid_rfid(attrs.get("tray_uuid")) or valid_rfid(attrs.get("tag_uid"))

    def active_slot_key(self) -> str | None:
        return next((s["key"] for s in self.slots() if s["active"]), None)

    @property
    def current_tray(self):
        return self._state("active_tray")

    @property
    def low_threshold(self) -> int:
        return self.entry.options.get(CONF_NOTIFY_FILAMENT_LOW, DEFAULT_FILAMENT_LOW)

    def _conf(self, key: str) -> Any:
        """Option value, falling back to the initial config data."""
        if key in self.entry.options:
            return self.entry.options[key]
        return self.entry.data.get(key)

    @property
    def price_per_kwh(self) -> float:
        """Electricity price from the price entity, else the fixed option."""
        entity_id = self._conf(CONF_PRICE_ENTITY)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is not None:
            try:
                return float(state.state)
            except ValueError:
                pass
        return self.entry.options.get(CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH)

    def _external_float(self, conf_key: str) -> float | None:
        entity_id = self._conf(conf_key)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None or state.state in UNAVAILABLE:
            return None
        try:
            return float(state.state)
        except ValueError:
            return None

    def entity_id(self, key: str, domain: str = "sensor") -> str | None:
        """Resolve a ha-bambulab entity by its unique id."""
        return er.async_get(self.hass).async_get_entity_id(
            domain, BAMBU_DOMAIN, f"{self.serial}_{key}"
        )

    def _state(self, key: str):
        entity_id = self.entity_id(key)
        return self.hass.states.get(entity_id) if entity_id else None

    def _value(self, key: str) -> str | None:
        state = self._state(key)
        return None if state is None or state.state in UNAVAILABLE else state.state

    def _float(self, key: str) -> float | None:
        value = self._value(key)
        try:
            return float(value) if value is not None else None
        except ValueError:
            return None

    def _minutes(self, key: str) -> float | None:
        """A duration entity in minutes. ha-bambulab stores minutes but suggests hours, so the
        entity usually shows hours: convert from the unit it reports."""
        state = self._state(key)
        if state is None:
            return None
        return to_minutes(self._float(key), state.attributes.get("unit_of_measurement"))

    async def async_start(self) -> None:
        data = await self._store.async_load()
        if data:
            self.history = PrintHistory(data.get("records"))
        watched = [
            eid
            for eid in (
                self.entity_id("print_status"),
                self.entity_id("active_tray"),
                self.entity_id("print_progress"),
                *self.slot_entities().values(),
            )
            if eid
        ]
        self.entry.async_on_unload(
            async_track_state_change_event(self.hass, watched, self._on_change)
        )
        # The entities may not be ready yet at setup: look for a running print a little later as well.
        @callback
        def _later(_now: datetime) -> None:
            self._ensure_session()

        self.entry.async_on_unload(async_call_later(self.hass, 30, _later))
        self.entry.async_on_unload(async_call_later(self.hass, 120, _later))
        if self.entry.options.get(CONF_AUTO_IMPORT, True):
            slot_ids = list(self.slot_entities().values())
            if slot_ids:
                self.entry.async_on_unload(
                    async_track_state_change_event(
                        self.hass, slot_ids, self._on_slot_change
                    )
                )
                self.import_from_ams(include_untagged=False)
        extra = [
            eid
            for eid in (self._conf(CONF_POWER_ENTITY), self._conf(CONF_PRICE_ENTITY))
            if eid
        ]
        if extra:
            self.entry.async_on_unload(
                async_track_state_change_event(self.hass, extra, self._on_external)
            )

    @callback
    def _on_slot_change(self, event: Event) -> None:
        """A tray changed: link or create the spool if a new tagged spool appeared."""
        if event.data["new_state"] is not None:
            self.import_from_ams(include_untagged=False)

    @callback
    def _on_external(self, event: Event) -> None:
        """Power or price entity changed."""
        if event.data["entity_id"] == self._conf(CONF_POWER_ENTITY):
            session = self.history.session
            if session is not None:
                session.add_power(
                    dt_util.utcnow(), self._external_float(CONF_POWER_ENTITY)
                )
        async_dispatcher_send(self.hass, self.signal)

    @callback
    def _on_change(self, event: Event) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        if new is None:
            return
        entity_id = event.data["entity_id"]
        if entity_id != self.entity_id("print_status"):
            self._ensure_session()
        if entity_id == self.entity_id("print_status"):
            self._on_status(old.state if old else None, new.state)
        elif entity_id == self.entity_id("print_progress"):
            self._on_progress()
        elif entity_id == self.entity_id("active_tray"):
            self._on_tray(new.attributes)
            self._note_slot()
            async_dispatcher_send(self.hass, self.signal)
        else:
            # A slot changed (its "active" flag follows the tray change a moment later).
            self._note_slot()

    def shortages_now(self) -> list[dict[str, Any]]:
        """Spools of the running print that hold less than the print needs from them."""
        session = self.history.session
        if session is None or not session.start_slots:
            return []
        needs = session.plan or self._plan_by_slot()
        total = self._float("print_weight")
        if not needs and session.slot_key and total:
            needs = {session.slot_key: total}
        slots = {
            key: SlotInfo(key, start["material"], start["capacity_g"])
            for key, start in session.start_slots.items()
        }
        found = shortages(needs, slots)
        store = self.filament.store
        for item in found:
            spool = store.spools.get(session.start_slots[item["slot"]].get("spool_id") or "")
            item["spool"] = spool.name if spool else None
            item["spool_id"] = spool.id if spool else None
        return found

    def _warn_shortage(self) -> None:
        """Announce once per print that a spool will not last."""
        session = self.history.session
        if session is None or session.warned:
            return
        found = self.shortages_now()
        if not found:
            return
        session.warned = True
        for item in found:
            self.hass.bus.async_fire(
                EVENT_SPOOL_INSUFFICIENT,
                {"serial": self.serial, "print": session.name, **item},
            )

    @property
    def min_stock(self) -> dict[str, float]:
        try:
            return parse_prices(self._conf(CONF_MIN_STOCK))
        except ValueError:
            return {}

    def _check_stock(self) -> None:
        """Fire an event once per material when its total stock falls below the minimum."""
        totals = self.filament.store.stock_by_material()
        for material, minimum in self.min_stock.items():
            key = f"stock:{material}"
            have = totals.get(material, 0.0)
            if have >= minimum:
                self._low_notified.discard(key)
            elif key not in self._low_notified:
                self._low_notified.add(key)
                self.hass.bus.async_fire(
                    EVENT_STOCK_LOW,
                    {
                        "serial": self.serial,
                        "material": material,
                        "stock_g": have,
                        "minimum_g": minimum,
                    },
                )

    def rebook(self, started: str, spool_id: str | None) -> dict[str, Any]:
        """Charge a recorded print to another spool and move the stock accordingly."""
        store = self.filament.store
        spool = store.spools.get(spool_id) if spool_id else None
        if spool_id and spool is None:
            raise KeyError(spool_id)
        price = (
            spool.price_per_kg
            if spool is not None and spool.price_per_kg is not None
            else self.price_for_material(spool.material if spool else None)
        )
        previous, grams = self.history.rebook(
            started,
            spool.id if spool else None,
            spool.name if spool else None,
            price,
            spool.material if spool else None,
            spool.color if spool else None,
        )
        if previous != (spool.id if spool else None):
            store.restore(previous, grams)
            if spool is not None:
                store.consume(spool.id, grams)
                self._check_spool(spool)
            self._check_stock()
        self._store.async_delay_save(lambda: {"records": self.history.records}, 1)
        self.filament.changed()
        async_dispatcher_send(self.hass, self.signal)
        return self.history.find(started) or {}

    def _on_progress(self) -> None:
        """Remember the progress (the highest one: a stopped print resets it) and the slot plan."""
        session = self.history.session
        progress = self._float("print_progress")
        if session is None or progress is None:
            return
        session.progress = max(session.progress or 0.0, progress)
        if not session.plan:
            session.plan = self._plan_by_slot()
            if session.plan:
                self._warn_shortage()

    def _note_slot(self) -> None:
        """Record which slot is feeding the print, to split the filament over several spools."""
        session = self.history.session
        if session is not None:
            session.usage.note(self.active_slot_key(), session.progress)

    def _slot_snapshot(self) -> dict[str, dict[str, Any]]:
        """Per slot: the assigned spool and the remaining percent the AMS reports."""
        store = self.filament.store
        snapshot: dict[str, dict[str, Any]] = {}
        for key, entity_id in self.slot_entities().items():
            state = self.hass.states.get(entity_id)
            if state is None or "active" not in state.attributes:
                continue
            attrs = state.attributes
            spool = store.spool_for_slot(key)
            snapshot[key] = {
                "spool_id": spool.id if spool else None,
                "remain": attrs.get("remain") if attrs.get("remain_enabled", True) else None,
                "initial_g": spool.initial_weight_g if spool else None,
                "capacity_g": spool.remaining_g if spool else None,
                "material": (spool.material if spool else attrs.get("type")) or "",
            }
        return snapshot

    def _plan_by_slot(self) -> dict[str, float]:
        """Grams per slot the slicer planned, from the attributes of the print weight sensor."""
        state = self._state("print_weight")
        slots = self.slot_entities()
        plan: dict[str, float] = {}
        for name, grams in (state.attributes if state else {}).items():
            if isinstance(grams, bool) or not isinstance(grams, (int, float)):
                continue
            match = re.fullmatch(r"AMS (\d+) Tray (\d+)", str(name))
            if match:
                suffix = f"ams_{match[1]}_slot_{match[2]}"
                key = next((k for k, e in slots.items() if e.endswith(suffix)), None)
            elif str(name).startswith("External Spool"):
                key = next((k for k in slots if "ExternalSpool" in k), None)
            else:
                key = None
            if key:
                plan[key] = float(grams)
        return plan

    def _usages(
        self, session, outcome: str, total_g: float | None
    ) -> list[dict[str, Any]]:
        """Filament of the print per spool (see consumption.py); empty: charge the start spool."""
        if session is None or not total_g:
            return []
        end = self._slot_snapshot()
        slots = {
            key: SlotInfo(
                key,
                start["material"],
                start["capacity_g"],
                measured_grams(
                    start["remain"], end.get(key, {}).get("remain"), start["initial_g"]
                ),
            )
            for key, start in session.start_slots.items()
        }
        segments = session.usage.segments or (
            [Segment(session.slot_key, 0.0)] if session.slot_key else []
        )
        plan = session.plan or self._plan_by_slot()
        store = self.filament.store
        usages = []
        for part in split_usage(
            total_g,
            finished=outcome == STATUS_FINISH,
            progress=session.progress,
            segments=segments,
            slots=slots,
            plan=plan,
        ):
            start = session.start_slots.get(part.slot, {})
            spool = store.spools.get(start.get("spool_id")) if start.get("spool_id") else None
            material = (spool.material if spool else start.get("material")) or None
            price = (
                spool.price_per_kg
                if spool is not None and spool.price_per_kg is not None
                else self.price_for_material(material)
            )
            usages.append(
                {
                    "slot": part.slot,
                    "spool_id": spool.id if spool else None,
                    "spool_name": spool.name if spool else None,
                    "weight_g": part.grams,
                    "price_per_kg": price,
                    "material": material,
                    "color": spool.color if spool else None,
                }
            )
        usages.sort(key=lambda u: -u["weight_g"])
        return usages

    def _on_tray(self, attrs: dict[str, Any]) -> None:
        session = self.history.session
        if session is None or not attrs:
            return
        session.material = attrs.get("type") or session.material
        session.color = attrs.get("color") or session.color

    def _printer_start(self, now: datetime) -> datetime | None:
        """When the running print really started, from the printer's start time (None if not plausible)."""
        try:
            started = datetime.fromisoformat(str(self._value("start_time")))
        except (TypeError, ValueError):
            return None
        if started.tzinfo is None or started >= now or (now - started).total_seconds() > 48 * 3600:
            return None
        return started

    def _adopt_start(self, session: Any, now: datetime, progress: float | None) -> None:
        """Give a session that began late the printer's start time and the energy meter reading of that moment.

        Right after a restart the progress is often not known yet when the session begins, so this
        is tried again on every later change until the progress allows it. The start time of a
        print that has only just begun may still be the one of the previous job.
        """
        if session.start_checked or progress is None or progress < MIN_PROGRESS_FOR_START_TIME:
            return
        started = self._printer_start(now)
        if started is None:  # the start time sensor may not be ready yet right after a restart: try again later
            return
        session.start_checked = True
        if (session.started - started).total_seconds() > 120:
            session.started = started
            self.hass.async_create_task(self._backfill_energy(session, started))

    def _begin_session(self, now: datetime, progress: float = 0.0) -> None:
        """Fill the session that just began with the spool, the slots and the meters.

        A print that is already under way (Home Assistant restarted in the middle of it) keeps the
        printer's start time, and the meter reading of that moment is taken from the recorder.
        """
        tray = self._state("active_tray")
        if tray is not None:
            self._on_tray(tray.attributes)
        session = self.history.session
        if session is None:
            return
        self._adopt_start(session, now, progress)
        session.slot_key = self.active_slot_key()
        spool = self.filament.store.spool_for_slot(session.slot_key)
        if spool is not None:
            session.spool_id = spool.id
            session.spool_name = spool.name
            session.material = spool.material
            session.color = spool.color or session.color
        session.start_slots = self._slot_snapshot()
        session.progress = self._float("print_progress")
        session.plan = self._plan_by_slot()
        session.usage.note(session.slot_key, progress)
        self._warn_shortage()
        session.energy_start_kwh = self._external_float(CONF_ENERGY_ENTITY)
        session.add_power(now, self._external_float(CONF_POWER_ENTITY))

    async def _backfill_energy(self, session: Any, started: datetime) -> None:
        """Take the energy meter reading at the start of the print from the recorder."""
        entity = self._conf(CONF_ENERGY_ENTITY)
        if not entity:
            return
        try:
            from homeassistant.components.recorder import get_instance, history

            states = await get_instance(self.hass).async_add_executor_job(
                lambda: history.get_significant_states(
                    self.hass, started, started + timedelta(minutes=10), [entity],
                    include_start_time_state=True, significant_changes_only=False, no_attributes=True,
                )
            )
        except Exception:  # the recorder is optional; the energy then counts from the pick-up on
            _LOGGER.warning("Energy meter reading at the start not available from the recorder", exc_info=True)
            return
        _LOGGER.debug("Recorder returned %s for %s", states, entity)
        for state in states.get(entity, []):
            try:
                value = float(state.state)
            except (TypeError, ValueError):
                continue
            if self.history.session is session and (
                session.energy_start_kwh is None or value <= session.energy_start_kwh
            ):
                session.energy_start_kwh = value
            return

    def _adopt_spool(self) -> None:
        """Give a running session the spool of the active slot when it was not known at its start.

        Right after a restart of Home Assistant the slot entities may not be ready when the
        session begins; without a spool the print would be charged at the default price per kg
        and its filament taken from no spool at all.
        """
        session = self.history.session
        if session is None or session.spool_id is not None:
            return
        slot = self.active_slot_key()
        spool = self.filament.store.spool_for_slot(slot) if slot else None
        if spool is None:
            return
        session.slot_key = slot
        session.spool_id, session.spool_name = spool.id, spool.name
        session.material = spool.material
        session.color = spool.color or session.color
        if not session.start_slots:
            session.start_slots = self._slot_snapshot()
        if not session.usage.segments:
            session.usage.note(slot, self._float("print_progress") or 0.0)

    @callback
    def _ensure_session(self) -> None:
        """Pick up a print that is already running, e.g. after a restart of Home Assistant in the middle of it.

        Normally the change of the print status to "running" starts the session; when Home
        Assistant comes up during a print that change may never be seen. Without a session the
        print would be neither recorded nor charged to its spool.
        """
        if self.history.session is not None:
            self._adopt_start(self.history.session, dt_util.utcnow(), self._float("print_progress"))
            self._adopt_spool()
            return
        if self._value("print_status") not in ("running", "pause"):
            return
        now = dt_util.utcnow()
        outcome = self.history.update_status(None, "running", now, self._value("subtask_name"))
        if outcome == "started":
            self._begin_session(now, self._float("print_progress") or 0.0)

    @callback
    def _on_status(self, old: str | None, new: str) -> None:
        now = dt_util.utcnow()
        name = self._value("subtask_name")
        outcome = self.history.update_status(old, new, now, name)
        if outcome == "started":
            self._begin_session(now, self._float("print_progress") or 0.0)
            self.hass.bus.async_fire(
                EVENT_PRINT_STARTED, {"serial": self.serial, "name": name}
            )
        elif outcome is not None:
            weight_state = self._state("print_weight")
            session = self.history.session
            spool = (
                self.filament.store.spools.get(session.spool_id)
                if session and session.spool_id
                else None
            )
            price = (
                spool.price_per_kg
                if spool is not None and spool.price_per_kg is not None
                else self.price_for_material(session.material if session else None)
            )
            planned_g = self._float("print_weight")
            usages = self._usages(session, outcome, planned_g)
            record = self.history.finish(
                outcome,
                now,
                planned_g,
                dict(weight_state.attributes) if weight_state else None,
                price,
                name,
                self._external_float(CONF_ENERGY_ENTITY),
                self.price_per_kwh,
                usages,
                planned_g,
            )
            if record is not None:
                self.hass.bus.async_fire(
                    EVENT_PRINT_FAILED
                    if outcome == STATUS_FAILED
                    else EVENT_PRINT_FINISHED,
                    {"serial": self.serial, **record.as_dict()},
                )
                self._store.async_delay_save(
                    lambda: {"records": self.history.records}, 1
                )
                # Every spool the print used loses its share (the start spool, all of it, without a split).
                charged = (
                    [(u["spool_id"], u["weight_g"]) for u in usages if u["spool_id"]]
                    if usages
                    else ([(spool.id, planned_g)] if spool is not None else [])
                )
                for spool_id, grams in charged:
                    used = self.filament.store.consume(spool_id, grams)
                    if used is not None:
                        self._check_spool(used)
                if charged:
                    self._check_stock()
                    self.filament.changed()
                else:
                    self._check_filament()
        async_dispatcher_send(self.hass, self.signal)

    def _check_spool(self, spool) -> None:
        """Fire an event once per spool when its stock falls below the threshold."""
        key = f"spool:{spool.id}"
        if spool.remaining_g <= 0 and self.entry.options.get(CONF_AUTO_ARCHIVE, True):
            self.filament.store.archive(spool.id)
            self._low_notified.discard(key)
            self.hass.bus.async_fire(
                EVENT_SPOOL_EMPTY,
                {
                    "serial": self.serial,
                    "spool_id": spool.id,
                    "spool": spool.name,
                    "type": spool.material,
                    "color": spool.color,
                },
            )
            return
        if spool.remaining_percent > self.low_threshold:
            self._low_notified.discard(key)
        elif key not in self._low_notified:
            self._low_notified.add(key)
            self.hass.bus.async_fire(
                EVENT_FILAMENT_LOW,
                {
                    "serial": self.serial,
                    "spool_id": spool.id,
                    "spool": spool.name,
                    "remain": spool.remaining_percent,
                    "remaining_g": spool.remaining_g,
                    "type": spool.material,
                    "color": spool.color,
                    "replacement": (self._replacement(spool) or {}).get("name"),
                },
            )

    def _check_filament(self) -> None:
        """Fire an event once per spool when the remaining amount is low."""
        tray = self._state("active_tray")
        if tray is None:
            return
        attrs = tray.attributes
        remain = attrs.get("remain")
        key = attrs.get("tray_uuid") or tray.state
        if not isinstance(remain, (int, float)) or not attrs.get("remain_enabled", True):
            return
        if remain > self.low_threshold:
            self._low_notified.discard(key)
        elif key not in self._low_notified:
            self._low_notified.add(key)
            self.hass.bus.async_fire(
                EVENT_FILAMENT_LOW,
                {
                    "serial": self.serial,
                    "tray": tray.state,
                    "remain": remain,
                    "type": attrs.get("type"),
                    "color": attrs.get("color"),
                },
            )
