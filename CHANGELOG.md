# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/weskona/3D-Print-Assistant/compare/v0.3.0-beta.1...HEAD
[0.3.0-beta.1]: https://github.com/weskona/3D-Print-Assistant/compare/v0.2.0...v0.3.0-beta.1
[0.2.0]: https://github.com/weskona/3D-Print-Assistant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/weskona/3D-Print-Assistant/releases/tag/v0.1.0
