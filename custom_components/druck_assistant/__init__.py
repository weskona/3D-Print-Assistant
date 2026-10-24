"""3D-Druck-Assistant: print history, filament cost and events on top of ha-bambulab."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .tracker import PrintTracker

PLATFORMS = [Platform.SENSOR]

type DruckAssistantConfigEntry = ConfigEntry[PrintTracker]


async def async_setup_entry(hass: HomeAssistant, entry: DruckAssistantConfigEntry) -> bool:
    tracker = PrintTracker(hass, entry)
    await tracker.async_start()
    entry.runtime_data = tracker
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DruckAssistantConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload(hass: HomeAssistant, entry: DruckAssistantConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
