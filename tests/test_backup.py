"""The backup file: what goes in, and what a restore refuses."""

import importlib.util
from pathlib import Path

import pytest

PKG = Path(__file__).parent.parent / "custom_components" / "druck_assistant"
spec = importlib.util.spec_from_file_location("backup", PKG / "backup.py")
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)

FILAMENT = {"spools": [{"id": "a", "name": "A"}], "assignments": {}, "projects": []}
RECORDS = {"SN1": [{"started": "2026-01-01T10:00:00+00:00", "name": "Benchy"}]}


def make():
    return backup.make_backup(FILAMENT, RECORDS, "0.10.0-beta.6", "2026-10-30T10:00:00+00:00")


def test_a_backup_survives_a_round_trip():
    filament, records = backup.parse_backup(make())
    assert filament == FILAMENT
    assert records == RECORDS


def test_records_are_copied_into_the_backup():
    data = make()
    RECORDS["SN1"].append({"started": "x"})
    try:
        assert len(data["printers"]["SN1"]["records"]) == 1
    finally:
        RECORDS["SN1"].pop()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(format="other"),
        lambda d: d.update(version=99),
        lambda d: d.update(version="1"),
        lambda d: d.update(filament=[]),
        lambda d: d["filament"].update(spools=[{"name": "no id"}]),
        lambda d: d.update(printers=[]),
        lambda d: d["printers"]["SN1"].update(records=[{"name": "no start"}]),
        lambda d: d["printers"].update(SN2="x"),
    ],
)
def test_a_damaged_backup_is_refused(mutate):
    data = make()
    mutate(data)
    with pytest.raises(ValueError):
        backup.parse_backup(data)


def test_something_that_is_no_backup_is_refused():
    for data in (None, [], "x", {}, {"format": "druck_assistant_backup"}):
        with pytest.raises(ValueError):
            backup.parse_backup(data)
