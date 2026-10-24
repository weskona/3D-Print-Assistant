"""Websocket API used by the sidebar panel."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    WS_DATA,
    WS_SPOOL_ASSIGN,
    WS_SPOOL_DELETE,
    WS_SPOOL_SAVE,
)
from .spools import SpoolError


@callback
def async_register(hass: HomeAssistant) -> None:
    for command in (ws_get_data, ws_spool_save, ws_spool_delete, ws_spool_assign):
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
        },
    )


@websocket_api.websocket_command(
    {vol.Required("type"): WS_SPOOL_SAVE, vol.Required("spool"): dict}
)
@websocket_api.require_admin
@callback
def ws_spool_save(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    manager = hass.data[DOMAIN]["filament"]
    try:
        spool = manager.store.save_spool(msg["spool"])
    except SpoolError as err:
        connection.send_error(msg["id"], "invalid_spool", str(err))
        return
    manager.changed()
    connection.send_result(msg["id"], spool.as_dict())


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
        manager.store.assign(msg["slot_key"], msg["spool_id"])
    except SpoolError as err:
        connection.send_error(msg["id"], "unknown_spool", str(err))
        return
    manager.changed()
    connection.send_result(msg["id"])
