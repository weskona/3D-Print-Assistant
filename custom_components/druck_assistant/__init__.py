"""3D Print Assistant: print history, filament cost and events on top of ha-bambulab."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration
from homeassistant.util import dt as dt_util

from . import api
from .catalog_store import CatalogManager
from .const import DOMAIN, LOGGED_EVENTS, PANEL_COMPONENT, PANEL_URL_PATH, STATIC_URL
from .events import EventLog
from .filament import FilamentManager
from .tracker import PrintTracker

PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type DruckAssistantConfigEntry = ConfigEntry[PrintTracker]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    catalog = CatalogManager(hass)
    await catalog.async_load()
    manager = FilamentManager(hass)
    await manager.async_load(catalog.catalog)
    catalog.on_update = lambda: manager.use_catalog(catalog.catalog)
    event_store = Store(hass, 1, f"{DOMAIN}.events")
    events = EventLog((await event_store.async_load() or {}).get("entries"))
    hass.data[DOMAIN] = {"filament": manager, "catalog": catalog, "events": events, "event_store": event_store}

    @callback
    def _log_event(event: Event) -> None:
        kind = event.event_type.removeprefix(f"{DOMAIN}_")
        events.add(kind, dict(event.data), dt_util.utcnow().isoformat())
        event_store.async_delay_save(lambda: {"entries": events.entries}, 5)

    for event_type in LOGGED_EVENTS:
        hass.bus.async_listen(event_type, _log_event)

    async def _auto_update(now: datetime) -> None:
        """Once a week, when the setting asks for it."""
        if not manager.store.options.get("catalog_auto"):
            return
        last = catalog.updated_at
        if not last or now - datetime.fromisoformat(last) >= timedelta(days=7):
            await catalog.async_update()

    async_track_time_interval(hass, _auto_update, timedelta(hours=12))
    api.async_register(hass)
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                STATIC_URL, str(Path(__file__).parent / "frontend"), cache_headers=False
            )
        ]
    )
    return True


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
        sidebar_title="3D Print Assistant",
        sidebar_icon="mdi:printer-3d",
        require_admin=False,
        config={},
    )


async def _async_reload(hass: HomeAssistant, entry: DruckAssistantConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
