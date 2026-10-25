"""Track a ha-bambulab printer and keep print history."""

from __future__ import annotations

import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    BAMBU_DOMAIN,
    CONF_AUTO_ARCHIVE,
    CONF_AUTO_IMPORT,
    CONF_ENERGY_ENTITY,
    CONF_FILAMENT_PRICES,
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
    STATUS_FAILED,
    STORAGE_VERSION,
)
from .history import PrintHistory, parse_prices, price_for, to_minutes
from .spools import valid_rfid

UNAVAILABLE = ("unknown", "unavailable", None)


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
            },
            "current_print": self.current_print(),
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
                "price_per_kg": self.price_for_material(tray.attributes.get("type")),
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
                }
            )
        return sorted(slots, key=lambda s: s["key"])

    def import_from_ams(self, *, include_untagged: bool) -> dict[str, list[dict[str, Any]]]:
        """Create or link spools for the current AMS contents."""
        result: dict[str, list[dict[str, Any]]] = {
            "created": [], "assigned": [], "adopted": [],
        }
        for key, entity_id in self.slot_entities().items():
            state = self.hass.states.get(entity_id)
            if state is None or "active" not in state.attributes:
                continue
            action, spool = self.filament.store.import_slot(
                key, dict(state.attributes), include_untagged=include_untagged
            )
            if action in result and spool is not None:
                result[action].append({"slot": key, "spool": spool.as_dict()})
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
            for eid in (self.entity_id("print_status"), self.entity_id("active_tray"))
            if eid
        ]
        self.entry.async_on_unload(
            async_track_state_change_event(self.hass, watched, self._on_change)
        )
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
        if event.data["entity_id"] == self.entity_id("print_status"):
            self._on_status(old.state if old else None, new.state)
        else:
            self._on_tray(new.attributes)
            async_dispatcher_send(self.hass, self.signal)

    def _on_tray(self, attrs: dict[str, Any]) -> None:
        session = self.history.session
        if session is None or not attrs:
            return
        session.material = attrs.get("type") or session.material
        session.color = attrs.get("color") or session.color

    @callback
    def _on_status(self, old: str | None, new: str) -> None:
        now = dt_util.utcnow()
        name = self._value("subtask_name")
        outcome = self.history.update_status(old, new, now, name)
        if outcome == "started":
            tray = self._state("active_tray")
            if tray is not None:
                self._on_tray(tray.attributes)
            session = self.history.session
            if session is not None:
                session.slot_key = self.active_slot_key()
                spool = self.filament.store.spool_for_slot(session.slot_key)
                if spool is not None:
                    session.spool_id = spool.id
                    session.spool_name = spool.name
                    session.material = spool.material
                    session.color = spool.color or session.color
                session.energy_start_kwh = self._external_float(CONF_ENERGY_ENTITY)
                session.add_power(now, self._external_float(CONF_POWER_ENTITY))
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
            used_g = self._float("print_weight")
            record = self.history.finish(
                outcome,
                now,
                self._float("print_weight"),
                dict(weight_state.attributes) if weight_state else None,
                price,
                name,
                self._external_float(CONF_ENERGY_ENTITY),
                self.price_per_kwh,
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
                if spool is not None:
                    self.filament.store.consume(spool.id, used_g)
                    self._check_spool(spool)
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
