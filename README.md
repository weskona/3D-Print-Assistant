# 3D Print Assistant

[Deutsch](README.de.md)

> **Beta:** This project is in beta. Expect changes, and please report problems as issues.

Home Assistant integration for Bambu Lab printers. It builds on
[ha-bambulab](https://github.com/greghesp/ha-bambulab) and reads its entities
(print status, weight, active filament) instead of talking to the printer itself.

![Overview](docs/screenshots/overview.png)

## Features

- Print history (last 200 prints, persistent) with duration, result, weight, material and color
- Filament and electricity cost per print and in total (currency: euro)
- Filament price per type (e.g. `PLA=20`) with a default price per kg
- Electricity cost via an energy meter (kWh) or a power sensor (W, integrated over the print duration); fixed price or price from an entity
- Filament management: spool inventory with remaining weight, price and color, assigned to AMS/external spool slots; used filament is deducted after each print and low stock fires an event
- Own "3D Print Assistant" sidebar panel with totals, the print in progress (live stage, progress, times, layer, weight, temperatures, cost estimate, cover image), the live camera view of the printer, loaded filament and print history (updates live on print start and end)
- Events for automations: `druck_assistant_print_started`, `druck_assistant_print_finished`,
  `druck_assistant_print_failed`, `druck_assistant_filament_low` (with the suggested `replacement` spool), `druck_assistant_spool_imported`, `druck_assistant_spool_empty`,
  `druck_assistant_spool_insufficient` (a spool will not last for the running print), `druck_assistant_stock_low` (a type fell below its minimum stock)

## Filament management

Open the "Filament" tab of the panel (administrators can edit) and add your spools, then assign
each spool to a slot of the printer in the "AMS" tab. The spool's price replaces the type price, and the
used weight is deducted when the print ends.

**Consumption:** the weight is split over all spools a print used. The add-on follows the active slot during the
print (multi color) and uses the grams per slot of the slicer when ha-bambulab reports them (attributes of the print
weight sensor). When a spool runs empty and the AMS continues with another spool of the same filament, the first
spool is charged only what was left on it and the rest goes to the refill spool; without other data the remaining
percent the AMS reports per slot decides. A print that did not finish counts only for the progress it reached.
Each spool is charged with its own price; the print history lists the spools of such a print.

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
rows) with the total stock of all its spools, the average price per kg and the average cost per kg of the recorded prints ("Avg. printed", also shown for archived spools and for the spool in an AMS slot). Click the name of a type with several spools to
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
**Weighing and calibration:** the scale button of a spool takes the weight on the scale and turns it into the filament
left (it subtracts the empty spool: 250 g for Bambu Lab, 200 g otherwise, or the value you enter). The real empty weight
is kept per spool. A spool's form has more details: purchase date, shop, order number, batch, location and last drying.
A label with name, type, color, weight and place can be printed from the label button of a row.

**Before the print:** when a spool holds less than the print needs from it, the Overview tab shows a warning and
`druck_assistant_spool_insufficient` fires once. It names a slot with the same filament that can take over, if there is one.
For a spool that is almost empty the AMS tab (and the low-filament event) suggests a replacement from your stock.

**Stock and shopping list:** set a minimum stock per type in the integration options (one per line, e.g. `PLA=2000`).
The Filament tab then shows the stock per type, what is missing, the estimated cost and how many days the stock lasts
at your consumption of the last 30 days, with a button that copies the shopping list. `druck_assistant_stock_low` fires
once when a type falls below its minimum.

**Corrections, statistics and lists:** the arrows button of a print in the history charges it to another spool and moves the
filament. The "Statistics" tab shows cost, filament, failure rate and wasted money per material, the cost per month (split into filament and electricity), the most
expensive prints and the price per kg of your purchases. Spools and the history can be exported as CSV, and spools can be imported from a CSV file.
A spool is shared by all printers.

## Installation

1. Install ha-bambulab and set up your printer.
2. Copy `custom_components/druck_assistant` to `config/custom_components/` (or add this repository as a custom repository in HACS).
3. Restart Home Assistant, add the "3D Print Assistant" integration and select the printer.
4. Set filament prices, electricity price and the low filament threshold in the integration options.

## Design

The panel is always dark and independent of the Home Assistant theme. Its look is inspired by
[glow-dashboard](https://github.com/deepblue120/glow-dashboard) (colors, rounded cards, pill tabs); the code is our own.
The font is [Outfit](https://github.com/Outfitio/Outfit-Fonts) under the SIL Open Font License
(`custom_components/druck_assistant/frontend/fonts/OFL-Outfit.txt`). More screenshots: `docs/screenshots/`.

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
