"""Sensors for the 3D Print Assistant integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy, UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DruckAssistantConfigEntry
from .const import BAMBU_DOMAIN, DOMAIN
from .history import PrintHistory
from .tracker import PrintTracker


@dataclass(frozen=True, kw_only=True)
class DruckSensorDescription(SensorEntityDescription):
    value_fn: Callable[[PrintHistory], Any] = lambda h: None
    tracker_fn: Callable[[PrintTracker], Any] | None = None
    tracker_attrs_fn: Callable[[PrintTracker], dict[str, Any]] | None = None
    attrs_fn: Callable[[PrintHistory], dict[str, Any]] | None = None


def _last(history: PrintHistory) -> dict[str, Any] | None:
    return history.records[-1] if history.records else None


SENSORS: tuple[DruckSensorDescription, ...] = (
    DruckSensorDescription(
        key="total_prints",
        translation_key="total_prints",
        icon="mdi:printer-3d",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda h: h.total_prints,
    ),
    DruckSensorDescription(
        key="successful_prints",
        translation_key="successful_prints",
        icon="mdi:check-circle-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda h: h.successful_prints,
    ),
    DruckSensorDescription(
        key="total_filament",
        translation_key="total_filament",
        native_unit_of_measurement=UnitOfMass.GRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda h: h.total_weight_g,
    ),
    DruckSensorDescription(
        key="total_cost",
        translation_key="total_cost",
        icon="mdi:cash",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda h: h.total_cost,
    ),
    DruckSensorDescription(
        key="total_energy",
        translation_key="total_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda h: h.total_energy_kwh,
    ),
    DruckSensorDescription(
        key="total_energy_cost",
        translation_key="total_energy_cost",
        icon="mdi:flash",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda h: h.total_energy_cost,
    ),
    DruckSensorDescription(
        key="electricity_price",
        translation_key="electricity_price",
        icon="mdi:currency-eur",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        suggested_display_precision=4,
        tracker_fn=lambda t: t.price_per_kwh,
    ),
    DruckSensorDescription(
        key="current_filament",
        translation_key="current_filament",
        icon="mdi:printer-3d-nozzle",
        tracker_fn=lambda t: (t.current_tray.attributes.get("type") if t.current_tray else None),
        tracker_attrs_fn=lambda t: (
            {
                "name": t.current_tray.attributes.get("name"),
                "color": t.current_tray.attributes.get("color"),
                "remain": t.current_tray.attributes.get("remain"),
                "price_per_kg": t.price_for_material(t.current_tray.attributes.get("type")),
            }
            if t.current_tray
            else {}
        ),
    ),
    DruckSensorDescription(
        key="last_print",
        translation_key="last_print",
        icon="mdi:history",
        value_fn=lambda h: (_last(h) or {}).get("name"),
        attrs_fn=lambda h: {
            "last": _last(h),
            "history": h.records[-20:][::-1],
        },
    ),
    DruckSensorDescription(
        key="last_print_cost",
        translation_key="last_print_cost",
        icon="mdi:cash-register",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        suggested_display_precision=2,
        value_fn=lambda h: (_last(h) or {}).get("cost"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DruckAssistantConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    tracker = entry.runtime_data
    async_add_entities(DruckSensor(tracker, desc) for desc in SENSORS)


class DruckSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: DruckSensorDescription

    def __init__(self, tracker: PrintTracker, description: DruckSensorDescription) -> None:
        self.entity_description = description
        self._tracker = tracker
        self._attr_unique_id = f"{tracker.serial}_{description.key}"
        # Attach to the printer device created by ha-bambulab.
        self._attr_device_info = DeviceInfo(identifiers={(BAMBU_DOMAIN, tracker.serial)})

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._tracker.signal, self.async_write_ha_state
            )
        )

    @property
    def native_value(self) -> Any:
        desc = self.entity_description
        if desc.tracker_fn is not None:
            return desc.tracker_fn(self._tracker)
        return desc.value_fn(self._tracker.history)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        desc = self.entity_description
        if desc.tracker_attrs_fn is not None:
            return desc.tracker_attrs_fn(self._tracker)
        fn = desc.attrs_fn
        return fn(self._tracker.history) if fn else None
