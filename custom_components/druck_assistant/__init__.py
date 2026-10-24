"""3D-Druck-Assistant: print history, filament cost and events on top of ha-bambulab."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from .const import DOMAIN, PANEL_COMPONENT, PANEL_URL_PATH, STATIC_URL, WS_DATA
from .tracker import PrintTracker

PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type DruckAssistantConfigEntry = ConfigEntry[PrintTracker]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    websocket_api.async_register_command(hass, ws_get_data)
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                STATIC_URL, str(Path(__file__).parent / "frontend"), cache_headers=False
            )
        ]
    )
    return True


@websocket_api.websocket_command({vol.Required("type"): WS_DATA})
@callback
def ws_get_data(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return history and totals of all configured printers."""
    printers = [
        entry.runtime_data.panel_data()
        for entry in hass.config_entries.async_loaded_entries(DOMAIN)
    ]
    connection.send_result(msg["id"], {"printers": printers})


async def async_setup_entry(hass: HomeAssistant, entry: DruckAssistantConfigEntry) -> bool:
    tracker = PrintTracker(hass, entry)
    await tracker.async_start()
    entry.runtime_data = tracker
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await _async_register_panel(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DruckAssistantConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    remaining = [
        e for e in hass.config_entries.async_loaded_entries(DOMAIN) if e is not entry
    ]
    if unloaded and not remaining:
        frontend.async_remove_panel(hass, PANEL_URL_PATH)
    return unloaded


async def _async_register_panel(hass: HomeAssistant) -> None:
    """Add the sidebar panel (once, shared by all printers)."""
    if PANEL_URL_PATH in hass.data.get(frontend.DATA_PANELS, {}):
        return
    version = (await async_get_integration(hass, DOMAIN)).version
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_COMPONENT,
        frontend_url_path=PANEL_URL_PATH,
        module_url=f"{STATIC_URL}/{PANEL_COMPONENT}.js?v={version}",
        sidebar_title="3D-Druck",
        sidebar_icon="mdi:printer-3d",
        require_admin=False,
        config={},
    )


async def _async_reload(hass: HomeAssistant, entry: DruckAssistantConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
