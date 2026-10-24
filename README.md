# 3D-Druck-Assistant

[Deutsch](README.de.md)

Home Assistant integration for Bambu Lab printers. It builds on
[ha-bambulab](https://github.com/greghesp/ha-bambulab) and reads its entities
(print status, weight, active filament) instead of talking to the printer itself.

## Features

- Print history (last 200 prints, persistent) with duration, result, weight, material and color
- Filament and electricity cost per print and in total (currency: euro)
- Filament price per type (e.g. `PLA=20`) with a default price per kg
- Electricity cost via an energy meter (kWh) or a power sensor (W, integrated over the print duration); fixed price or price from an entity
- Own "3D Printing" sidebar panel with totals, current print/filament and print history (updates live on print start and end)
- Events for automations: `druck_assistant_print_started`, `druck_assistant_print_finished`,
  `druck_assistant_print_failed`, `druck_assistant_filament_low`

## Installation

1. Install ha-bambulab and set up your printer.
2. Copy `custom_components/druck_assistant` to `config/custom_components/` (or add this repository as a custom repository in HACS).
3. Restart Home Assistant, add the "3D-Druck-Assistant" integration and select the printer.
4. Set filament prices, electricity price and the low filament threshold in the integration options.

## Languages

The source language is English. The integration ships with a German translation pack
(`translations/de.json` and the panel), which is picked automatically from the Home Assistant language.
To add a language, add a `translations/<lang>.json` file and a block in `TRANSLATIONS` in
`frontend/druck-assistant-panel.js`.

## Release

On every push to `main`, the workflow `.github/workflows/release.yml` checks the version in
`custom_components/druck_assistant/manifest.json`. If there is no tag `v<version>` yet, it creates
the tag and a GitHub release with `druck_assistant.zip`. The release notes come from the matching
`## [<version>]` section of `CHANGELOG.md`, otherwise they are generated automatically.
To publish, bump the manifest version and rename `## [Unreleased]` to `## [<version>] - <date>`.
