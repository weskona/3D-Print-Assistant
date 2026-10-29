"""The filament catalog: the bundled data, overlaid with what the last update downloaded."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store

from .catalog import load_catalog
from .catalog_update import (
    BRANDS,
    SPOOLMANDB_URL,
    STUDIO_URL,
    CatalogError,
    build_third_party,
    merge_bambu,
    parse_studio,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MAX_BYTES = 8 * 1024 * 1024
TIMEOUT = aiohttp.ClientTimeout(total=60)
BAMBU = "Bambu Lab"


class CatalogManager:
    """Serves the catalog and refreshes it from Bambu Studio and SpoolmanDB on request."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store = Store(hass, 1, f"{DOMAIN}.catalog")
        self._bundled: dict[str, Any] = {"products": []}
        self._overlay: dict[str, Any] = {}
        self._catalog: dict[str, Any] | None = None
        self._busy = False
        self.error = ""
        self.on_update: Any = None  # called after a successful update

    async def async_load(self) -> None:
        self._bundled = await self.hass.async_add_executor_job(load_catalog)
        self._overlay = await self._store.async_load() or {}
        self._catalog = None

    def _bundled_products(self, bambu: bool) -> list[dict[str, Any]]:
        return [p for p in self._bundled["products"] if (p.get("brand") == BAMBU) == bambu]

    @property
    def catalog(self) -> dict[str, Any]:
        if self._catalog is None:
            self._catalog = {
                "products": (self._overlay.get("bambu") or self._bundled_products(True))
                + (self._overlay.get("third_party") or self._bundled_products(False))
            }
        return self._catalog

    @property
    def updated_at(self) -> str:
        return str(self._overlay.get("updated_at") or "")

    def status(self) -> dict[str, Any]:
        products = self.catalog["products"]
        return {
            "bundled": self._bundled.get("retrieved", {}),
            "updated_at": self.updated_at,
            "products": len(products),
            "colors": sum(len(p.get("colors", [])) for p in products),
            "error": self.error,
            "busy": self._busy,
        }

    async def _fetch(self, url: str) -> Any:
        session = async_get_clientsession(self.hass)
        async with session.get(url, timeout=TIMEOUT) as response:
            response.raise_for_status()
            if response.content_length and response.content_length > MAX_BYTES:
                raise CatalogError("download too large")
            body = await response.content.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise CatalogError("download too large")
        return json.loads(body)

    async def async_update(self) -> dict[str, Any]:
        """Download both sources and keep the result; the old catalog stays when anything is wrong."""
        if self._busy:
            return self.status()
        self._busy = True
        try:
            studio = parse_studio(await self._fetch(STUDIO_URL))
            files: dict[str, Any] = {}
            for key in BRANDS:
                try:
                    files[key] = await self._fetch(SPOOLMANDB_URL.format(key=key))
                except (aiohttp.ClientError, TimeoutError, ValueError, CatalogError) as err:
                    _LOGGER.warning("SpoolmanDB file %s not updated: %s", key, err)
            third_party = build_third_party(files)
            got = {p["brand"] for p in third_party}
            # A manufacturer whose file could not be loaded keeps its bundled products.
            third_party += [p for p in self._bundled_products(False) if p.get("brand") not in got]
            self._overlay = {
                "updated_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "bambu": merge_bambu(self._bundled_products(True), studio),
                "third_party": third_party,
            }
            await self._store.async_save(self._overlay)
            self._catalog = None
            self.error = ""
            if self.on_update:
                self.on_update()
        except (aiohttp.ClientError, TimeoutError, ValueError, CatalogError) as err:
            self.error = str(err) or type(err).__name__
            _LOGGER.warning("Filament catalog not updated: %s", self.error)
        finally:
            self._busy = False
        return self.status()
