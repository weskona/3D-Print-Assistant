"""Websocket API used by the sidebar panel."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    WS_CATALOG,
    WS_DATA,
    WS_IMPORT_AMS,
    WS_SPOOL_ARCHIVE,
    WS_RECORD_REBOOK,
    WS_SPOOL_ASSIGN,
    WS_SPOOL_DELETE,
    WS_SPOOL_IMPORT,
    WS_SPOOL_SAVE,
    WS_SPOOL_WEIGH,
)
from .catalog import load_catalog
from .spools import SpoolError


@callback
def async_register(hass: HomeAssistant) -> None:
    for command in (
        ws_get_data,
        ws_spool_save,
        ws_spool_delete,
        ws_spool_assign,
        ws_import_ams,
        ws_catalog,
        ws_spool_archive,
        ws_spool_weigh,
        ws_spool_import,
        ws_record_rebook,
    ):
        websocket_api.async_register_command(hass, command)


@websocket_api.websocket_command({vol.Required("type"): WS_DATA})
@callback
def ws_get_data(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return history, totals and filament inventory of all configured printers."""
    manager = hass.data[DOMAIN]["filament"]
    printers = [
        entry.runtime_data.panel_data()
        for entry in hass.config_entries.async_loaded_entries(DOMAIN)
    ]
    connection.send_result(
        msg["id"],
        {
            "printers": printers,
            "spools": [s.as_dict() for s in manager.store.spools.values()],
            "min_stock": {
                material: minimum
                for entry in hass.config_entries.async_loaded_entries(DOMAIN)
                for material, minimum in entry.runtime_data.min_stock.items()
            },
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SPOOL_SAVE,
        vol.Required("spool"): dict,
        vol.Optional("quantity", default=1): vol.All(int, vol.Range(min=1, max=50)),
    }
)
@websocket_api.require_admin
@callback
def ws_spool_save(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    manager = hass.data[DOMAIN]["filament"]
    try:
        if msg["spool"].get("id"):
            created = [manager.store.save_spool(msg["spool"])]
        elif msg["quantity"] == 1:
            created = [manager.store.save_spool(msg["spool"])]
        else:
            created = manager.store.add_spools(msg["spool"], msg["quantity"])
    except SpoolError as err:
        connection.send_error(msg["id"], "invalid_spool", str(err))
        return
    manager.changed()
    connection.send_result(msg["id"], {"spools": [s.as_dict() for s in created]})


@websocket_api.websocket_command(
    {vol.Required("type"): WS_SPOOL_DELETE, vol.Required("spool_id"): str}
)
@websocket_api.require_admin
@callback
def ws_spool_delete(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    manager = hass.data[DOMAIN]["filament"]
    try:
        manager.store.delete_spool(msg["spool_id"])
    except SpoolError as err:
        connection.send_error(msg["id"], "unknown_spool", str(err))
        return
    manager.changed()
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SPOOL_ASSIGN,
        vol.Required("slot_key"): str,
        vol.Required("spool_id"): vol.Any(str, None),
    }
)
@websocket_api.require_admin
@callback
def ws_spool_assign(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    manager = hass.data[DOMAIN]["filament"]
    try:
        tag = next(
            (
                entry.runtime_data.slot_tag(msg["slot_key"])
                for entry in hass.config_entries.async_loaded_entries(DOMAIN)
                if msg["slot_key"] in entry.runtime_data.slot_entities()
            ),
            "",
        )
        manager.store.assign(msg["slot_key"], msg["spool_id"], tag)
    except SpoolError as err:
        connection.send_error(msg["id"], "unknown_spool", str(err))
        return
    manager.changed()
    connection.send_result(msg["id"])


@websocket_api.websocket_command({vol.Required("type"): WS_IMPORT_AMS})
@websocket_api.require_admin
@callback
def ws_import_ams(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Create or link spools for everything currently loaded in the AMS."""
    counts = {"created": 0, "assigned": 0, "adopted": 0, "synced": 0}
    for entry in hass.config_entries.async_loaded_entries(DOMAIN):
        for action, items in entry.runtime_data.import_from_ams(
            include_untagged=True
        ).items():
            counts[action] += len(items)
    connection.send_result(msg["id"], counts)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SPOOL_ARCHIVE,
        vol.Required("spool_id"): str,
        vol.Required("archived"): bool,
    }
)
@websocket_api.require_admin
@callback
def ws_spool_archive(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Archive a spool or restore it from the archive."""
    manager = hass.data[DOMAIN]["filament"]
    try:
        manager.store.archive(msg["spool_id"], msg["archived"])
    except SpoolError as err:
        connection.send_error(msg["id"], "unknown_spool", str(err))
        return
    manager.changed()
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SPOOL_WEIGH,
        vol.Required("spool_id"): str,
        vol.Required("gross_g"): vol.Any(int, float, str),
        vol.Optional("tare_g"): vol.Any(int, float, str, None),
    }
)
@websocket_api.require_admin
@callback
def ws_spool_weigh(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Set the remaining filament of a spool from its weight on a scale."""
    manager = hass.data[DOMAIN]["filament"]
    try:
        spool = manager.store.weigh(msg["spool_id"], msg["gross_g"], msg.get("tare_g"))
    except SpoolError as err:
        connection.send_error(msg["id"], "invalid_spool", str(err))
        return
    manager.changed()
    connection.send_result(msg["id"], {"spool": spool.as_dict()})


@websocket_api.websocket_command(
    {vol.Required("type"): WS_SPOOL_IMPORT, vol.Required("spools"): [dict]}
)
@websocket_api.require_admin
@callback
def ws_spool_import(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Create several spools at once (the rows of an imported list)."""
    manager = hass.data[DOMAIN]["filament"]
    created, errors = [], []
    for index, row in enumerate(msg["spools"][:500], start=1):
        try:
            created.append(manager.store.save_spool({k: v for k, v in row.items() if k != "id"}))
        except SpoolError as err:
            errors.append({"row": index, "error": str(err)})
    if created:
        manager.changed()
    connection.send_result(msg["id"], {"created": len(created), "errors": errors})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_RECORD_REBOOK,
        vol.Required("started"): str,
        vol.Required("spool_id"): vol.Any(str, None),
    }
)
@websocket_api.require_admin
@callback
def ws_record_rebook(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Charge a recorded print to another spool (its filament moves from the old spool)."""
    for entry in hass.config_entries.async_loaded_entries(DOMAIN):
        tracker = entry.runtime_data
        if tracker.history.find(msg["started"]) is None:
            continue
        try:
            record = tracker.rebook(msg["started"], msg["spool_id"])
        except KeyError:
            connection.send_error(msg["id"], "unknown_spool", "unknown spool")
        except ValueError as err:
            connection.send_error(msg["id"], "not_possible", str(err))
        else:
            connection.send_result(msg["id"], {"record": record})
        return
    connection.send_error(msg["id"], "unknown_record", "unknown print")


@websocket_api.websocket_command({vol.Required("type"): WS_CATALOG})
@websocket_api.async_response
async def ws_catalog(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return the filament catalog of Bambu Lab and other manufacturers (read once, then cached)."""
    domain_data = hass.data[DOMAIN]
    if "catalog" not in domain_data:
        domain_data["catalog"] = await hass.async_add_executor_job(load_catalog)
    connection.send_result(msg["id"], domain_data["catalog"])
