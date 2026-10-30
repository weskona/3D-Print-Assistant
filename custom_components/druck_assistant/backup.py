"""Home Assistant independent backup file of the inventory and the print history."""

from __future__ import annotations

from typing import Any

BACKUP_FORMAT = "druck_assistant_backup"
BACKUP_VERSION = 1


def make_backup(
    filament: dict[str, Any],
    records: dict[str, list[dict[str, Any]]],
    app_version: str,
    created: str,
) -> dict[str, Any]:
    """The backup: the spool inventory (with projects and settings) and the history of every printer by serial."""
    return {
        "format": BACKUP_FORMAT,
        "version": BACKUP_VERSION,
        "app_version": app_version,
        "created": created,
        "filament": filament,
        "printers": {serial: {"records": list(items)} for serial, items in records.items()},
    }


def parse_backup(data: Any) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    """Check a backup and return (filament data, records by printer serial); ValueError if it is not usable."""
    if not isinstance(data, dict) or data.get("format") != BACKUP_FORMAT:
        raise ValueError("not a backup of the 3D Print Assistant")
    version = data.get("version")
    if not isinstance(version, int) or version > BACKUP_VERSION:
        raise ValueError("the backup was made by a newer version")
    filament = data.get("filament")
    if not isinstance(filament, dict) or not isinstance(filament.get("spools", []), list):
        raise ValueError("the inventory in the backup is damaged")
    for spool in filament.get("spools", []):
        if not isinstance(spool, dict) or not isinstance(spool.get("id"), str):
            raise ValueError("the inventory in the backup is damaged")
    printers = data.get("printers")
    if not isinstance(printers, dict):
        raise ValueError("the history in the backup is damaged")
    records: dict[str, list[dict[str, Any]]] = {}
    for serial, item in printers.items():
        items = item.get("records") if isinstance(item, dict) else None
        if not isinstance(items, list) or not all(isinstance(r, dict) and isinstance(r.get("started"), str) for r in items):
            raise ValueError("the history in the backup is damaged")
        records[str(serial)] = items
    return filament, records
