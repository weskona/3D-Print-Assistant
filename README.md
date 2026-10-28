# 3D Print Assistant

[Deutsch](README.de.md)

> **Beta:** This project is in beta. Expect changes, and please report problems as issues.

Home Assistant integration for Bambu Lab printers. It builds on
[ha-bambulab](https://github.com/greghesp/ha-bambulab) and reads its entities
(print status, weight, active filament) instead of talking to the printer itself.

## Features

- Print history (last 200 prints, persistent) with duration, result, weight, material and color
- Filament and electricity cost per print and in total (currency: euro)
- Filament price per type (e.g. `PLA=20`) with a default price per kg
- Electricity cost via an energy meter (kWh) or a power sensor (W, integrated over the print duration); fixed price or price from an entity
- Filament management: spool inventory with remaining weight, price and color, assigned to AMS/external spool slots; used filament is deducted after each print and low stock fires an event
- Own "3D Print Assistant" sidebar panel with totals, the print in progress (live stage, progress, times, layer, weight, temperatures, cost estimate), loaded filament and print history (updates live on print start and end)
- Events for automations: `druck_assistant_print_started`, `druck_assistant_print_finished`,
  `druck_assistant_print_failed`, `druck_assistant_filament_low`, `druck_assistant_spool_imported`, `druck_assistant_spool_empty`

## Filament management

Open the "Filament" tab of the panel (administrators can edit) and add your spools, then assign
each spool to a slot of the printer in the "AMS" tab. The slot with the active spool at print start is used:
its spool's price replaces the type price, and the used weight is deducted when the print ends.
Click "Import from AMS" to create spools from the loaded AMS slots. New Bambu spools with an RFID
tag are also added automatically (option "Automatically add new Bambu spools"); spools without a
tag, such as third-party filament or the external spool, are only imported with the button.
The remaining stock of an imported spool is estimated from the AMS percentage, so correct it by hand if needed.
**Filter:** the Spools card has a search box (name, material, brand, notes, color) and filters for material,
brand and status (in stock, in a slot, low stock). The table and its totals show only the matching spools; the popup of a type still lists all of its spools.

**Adding a spool from the catalog:** in "Add spool", pick a manufacturer, a filament and a color from the
catalog to fill in name, material, brand and color; every field can still be changed. The catalog has Bambu Lab
(`docs/bambu-filaments.md`) and Anycubic, Creality, Elegoo, eSUN, Flashforge, Overture, Polymaker, Prusament and Sunlu
(`docs/third-party-filaments.md`, from the community database [SpoolmanDB](https://github.com/Donkie/SpoolmanDB), MIT license;
its hex values can be approximate).

**Editing spools:** the list shows one row per type and color (e.g. "Bambu PETG Basic" in black and in gray are two
rows) with the total stock of all its spools and the average price per kg. Click the name of a type with several spools to
expand and list them one by one. Spools are edited with the "Edit" button of their row; the edit popup also has Delete. A Bambu Lab spool in a slot can be edited once its RFID tag has been detected (the tag fills it in); spools in stock
and spools of other brands, which have no tag, can always be edited. A Bambu Lab spool without a tag that sits in a slot
can only be deleted from its row until the AMS detects it (spools are archived automatically when they run empty).

**Buying in bulk:** add the pack with "Add spool" and its quantity field (e.g. 4 x "PETG Basic Black", color black).
When a new Bambu spool is detected, the integration first looks for a matching spool in your stock
(not in a slot, no tag yet, same material, similar color) and uses it instead of creating a new one.
So the stock goes from 4 to 3 and the loaded spool is tracked from then on. Without a match, a new spool is created.
If the match is wrong, pick the right spool in the slot list of the AMS tab: the RFID tag moves to
it and the correction sticks. Choosing "none" stops the automatic assignment for the spool currently in
the slot (the "Import from AMS" button overrides this). You can also edit or clear a spool's RFID tag
in its form. A stock spool that lost its tag simply stays in stock.

A spool whose remaining stock reaches 0 g after a print is moved to the archive automatically
(option "Automatically archive empty spools") and fires `druck_assistant_spool_empty`. Restore
spools from the collapsible "Archived spools" list. Archived spools
are not imported or assigned again automatically, even if they are still loaded in the AMS.
Prints with several spools or materials are booked to the spool active at the start.

## Installation

1. Install ha-bambulab and set up your printer.
2. Copy `custom_components/druck_assistant` to `config/custom_components/` (or add this repository as a custom repository in HACS).
3. Restart Home Assistant, add the "3D Print Assistant" integration and select the printer.
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
While in beta, versions carry a `-beta.N` suffix (e.g. `0.2.0-beta.2`) and the release is marked as a pre-release.
To publish, bump the manifest version and rename `## [Unreleased]` to `## [<version>] - <date>`.
