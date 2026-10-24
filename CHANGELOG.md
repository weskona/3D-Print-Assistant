# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0-beta.3] - 2026-10-24

### Added

- Quantity when adding a spool: add a multi-pack (e.g. 4x PETG black) at once; the spools are numbered ("PETG Basic Black #1" to "#4").
- Stock matching: when a new spool is detected in the AMS, it is matched against spools you entered earlier (not in a slot, no RFID tag yet, same material, similar color) instead of creating a new one. The tag is stored on the matched spool, so a 4-pack goes from 4 to 3 spools in stock when the first one is loaded. Closest color wins, then the fullest spool; a stock spool without a color is a weaker match.
- Manual correction of the automatic match: choosing another spool for a slot moves the RFID tag to it, so the correction sticks; choosing "none" stops the automatic assignment for the tag currently in the slot (the "Import from AMS" button overrides this). The RFID tag of a spool can be edited or cleared in the spool form, and a tag is always carried by one spool only.
- Slots show an RFID badge when the tray reports a tag.

## [0.4.0-beta.2] - 2026-10-24

### Added

- Spool archive: spools can be archived and restored in the Filament tab; archived spools leave their slot and are listed in a collapsible "Archived spools" section.
- Empty spools (remaining stock 0 g after a print) are archived automatically. Can be turned off in the options.
- `druck_assistant_spool_empty` event when a spool is archived because it ran empty.

### Changed

- An archived spool that is still detected in the AMS is not imported again or restored automatically; restore it from the archive.

## [0.4.0-beta.1] - 2026-10-24

### Added

- Import spools from the AMS: new "Import from AMS" button in the Filament tab creates a spool for every loaded slot without a spool (type, name, color, weight and remaining stock are taken from the tray).
- Automatic import: a new Bambu spool with an RFID tag is added to the inventory and assigned to its slot as soon as it is detected. The tag is stored, so the same spool is recognized when it moves to another slot. A spool you assigned by hand to the slot is tagged instead of duplicated. Can be turned off in the options.
- `druck_assistant_spool_imported` event.

## [0.3.0-beta.1] - 2026-10-24

### Added

- Filament management: spool inventory (name, material, brand, color, price per kg, initial and remaining weight, notes) with a new "Filament" tab in the panel.
- Assign spools to AMS and external spool slots. After each print the used weight is deducted from the spool in the active slot, and the spool's price is used for the filament cost.
- `druck_assistant_filament_low` is also fired for assigned spools that fall below the low stock threshold; new sensor "Spools low on stock".
- Print history records the spool that was used.
- Websocket commands to manage spools (changes require an administrator).

### Changed

- The project is now in beta: versions carry a `-beta.N` suffix and releases are marked as pre-releases.


## [0.2.0] - 2026-10-24

### Added

- Own sidebar panel "3D Print Assistant" with totals, current print and filament, and print history.
- German language pack (config flow, entities and panel); English is the source language.
- German README (`README.de.md`).

### Changed

- The display name is now "3D Print Assistant" everywhere.
- Repository links point to the renamed repository `3D-Print-Assistant`.
- Python caches are no longer tracked (`.gitignore`).

## [0.1.0] - 2026-10-24

### Added

- Initial project setup with README.
- Changelog in Keep a Changelog format.
- Home Assistant integration `druck_assistant` on top of ha-bambulab: print history, filament usage and cost, sensors and events for print start, finish, failure and low filament.
- Electricity cost: optional energy meter (kWh) and power sensor (W) in the config flow, fixed or entity-based electricity price, new sensors for energy usage, energy cost and electricity price. Print cost now includes filament and electricity.
- Filament prices per type (e.g. `PLA=20`) in the options, sensor for the current filament including price per kg. Cost sensors in euro.
- GitHub workflow that creates a tag and release after a push to `main`.

[Unreleased]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.3...HEAD
[0.4.0-beta.3]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.2...v0.4.0-beta.3
[0.4.0-beta.2]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.1...v0.4.0-beta.2
[0.4.0-beta.1]: https://github.com/weskona/3D-Print-Assistant/compare/v0.3.0-beta.1...v0.4.0-beta.1
[0.3.0-beta.1]: https://github.com/weskona/3D-Print-Assistant/compare/v0.2.0...v0.3.0-beta.1
[0.2.0]: https://github.com/weskona/3D-Print-Assistant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/weskona/3D-Print-Assistant/releases/tag/v0.1.0
