"""Track a ha-bambulab printer and keep print history."""

from __future__ import annotations

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
    CONF_ENERGY_ENTITY,
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
    STATUS_FAILED,
    STORAGE_VERSION,
)
from .history import PrintHistory

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

    @property
    def price_per_kg(self) -> float:
        return self.entry.options.get(CONF_PRICE_PER_KG, DEFAULT_PRICE_PER_KG)

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
                session.energy_start_kwh = self._external_float(CONF_ENERGY_ENTITY)
                session.add_power(now, self._external_float(CONF_POWER_ENTITY))
            self.hass.bus.async_fire(
                EVENT_PRINT_STARTED, {"serial": self.serial, "name": name}
            )
        elif outcome is not None:
            weight_state = self._state("print_weight")
            record = self.history.finish(
                outcome,
                now,
                self._float("print_weight"),
                dict(weight_state.attributes) if weight_state else None,
                self.price_per_kg,
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
                self._check_filament()
        async_dispatcher_send(self.hass, self.signal)

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
