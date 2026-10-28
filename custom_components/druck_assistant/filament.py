"""Persistent filament inventory shared by all printers."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .catalog import color_index, load_catalog
from .const import DOMAIN, STORAGE_VERSION
from .spools import SpoolStore


class FilamentManager:
    """Loads, saves and announces changes of the spool inventory."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.store = SpoolStore()
        self.signal = f"{DOMAIN}_filament_update"
        self._storage: Store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.filament")

    async def async_load(self) -> None:
        data = await self._storage.async_load()
        if data:
            self.store = SpoolStore(**data)
        catalog = await self.hass.async_add_executor_job(load_catalog)
        self.store.colors = color_index(catalog)
        if self.store.backfill_notes():
            self.changed()

    @callback
    def changed(self) -> None:
        """Persist the inventory and notify listeners (sensors, panel)."""
        self._storage.async_delay_save(self.store.to_dict, 1)
        async_dispatcher_send(self.hass, self.signal)
