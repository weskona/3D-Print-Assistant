# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0-beta.6] - 2026-10-28

### Changed

- The archived spools list shows the spool color as a dot in front of the name, like the filament list.
- Prices per kg are shown in more places: the archived spools list has a Price column, and each AMS slot shows the price of its spool.
- The Overview tab shows the live camera view of the printer (ha-bambulab camera entity, MJPEG stream; it runs only while the tab is open) below the current print, and the cover image of the print while it is running.
- New "Avg. printed" column: the average filament cost per kg of the recorded prints of a type or spool (filament list, archived spools) and of the spool in an AMS slot.

## [0.7.0-beta.5] - 2026-10-28

### Fixed

- A new AMS spool stayed at its full weight: the AMS first reports an unknown remaining amount, so the spool was created as full, and the value reported a little later was never taken over. A spool that is still exactly full now takes the remaining amount the AMS reports; spools whose weight is tracked by prints are not touched.

## [0.7.0-beta.4] - 2026-10-28

### Fixed

- The stock matching of a new AMS spool was still too lenient within one product line: a pink Bambu PLA Matte was taken for a latte brown Bambu PLA Matte in stock because the colors were "close". Catalog spools carry the exact manufacturer color, so a stock spool with the same name now only matches a nearly identical color. Spools with other names keep the looser color match.

## [0.7.0-beta.3] - 2026-10-28

### Fixed

- A new spool in the AMS could be mistaken for a spool in stock: the automatic import matched an untagged stock spool by material and a similar color, so a red Bambu PLA Basic took over the tag of a plum Bambu PLA Matte instead of being added. Stock spools of another variant of the same product line (same brand and material, different variant name) are no longer matched.

## [0.7.0-beta.2] - 2026-10-28

### Added

- Spools can be archived by hand: the filament list has a new Archive button next to Edit and Delete. An archived spool leaves its slot and can be brought back with Restore in the archive.

## [0.7.0-beta.1] - 2026-10-28

### Changed

- New design of the panel, inspired by the look of [glow-dashboard](https://github.com/deepblue120/glow-dashboard): always dark (independent of the Home Assistant theme), rounded cards with letter-spaced titles, a pill tab bar, tiles with small labels and bold values, status chips, thick gradient progress bars and blurred popups. The font is Outfit (SIL Open Font License, files and license in `frontend/fonts`).
- Overview: two columns on wide screens (current print on the left, totals and history on the right, one column on narrow screens). The current print shows its progress as a large number with a status chip, and the print history is a list of rows (date, name with duration, material, weight and energy, total cost with the filament plus electricity split).
- AMS: the slots are tiles with color, material, remaining percent and the spool selection.

## [0.6.0-beta.2] - 2026-10-28

### Added

- The Overview tab shows the current stage of the printer (ha-bambulab's "Current stage" sensor, e.g. heating the hotend, auto bed leveling, printing) live in the "Current print" card, and in the idle card as well. The value follows the entity directly, so it changes the moment Home Assistant gets the new state, without waiting for the panel reload, and it uses Home Assistant's own translated state names.

## [0.6.0-beta.1] - 2026-10-26

### Added

- The filament catalog covers more manufacturers: Anycubic, Creality, Elegoo, eSUN, Flashforge, Overture, Polymaker, Prusament and Sunlu (103 filaments, 1,163 colors with hex values) next to Bambu Lab. The add spool form has a manufacturer select before filament and color, and uses the spool size of the product line when the catalog knows it. The data comes from the community database SpoolmanDB (MIT license, commit `8f1a99f9ca`, retrieved 2026-10-26) as `custom_components/druck_assistant/data/third_party_filaments.json` and a readable list in `docs/third-party-filaments.md`; `scripts/build_third_party_catalog.py` rebuilds it.

## [0.5.0-beta.8] - 2026-10-26

### Fixed

- The loaded filament in the Overview tab (and the `price_per_kg` attribute of the "Current filament" sensor) showed the default price per kg (25) instead of the price of the spool assigned to the active slot. It now uses the spool's price and falls back to the type price and the default only when the spool has none. The cost calculation of prints was not affected.

## [0.5.0-beta.7] - 2026-10-25

### Added

- The costs are split into filament and electricity: the total tile of the Overview tab shows "Filament x · Electricity y", the print history has separate columns for filament cost, electricity cost (with the kWh) and total, and there is a new sensor "Total filament cost". Records from before the split count their cost as filament cost.

### Fixed

- The remaining time of the current print was wrong: ha-bambulab reports it in minutes but suggests hours, so the entity usually shows hours (1.87 for 1 h 52 min) and the panel read that value as minutes. The panel now converts the value from the unit the entity reports (seconds, minutes, hours or days).

## [0.5.0-beta.6] - 2026-10-25

### Added

- The Overview tab shows the print in progress: name and status (printing, paused, preparing), progress bar, elapsed time, remaining time, finish time, layer, filament weight, nozzle and bed temperature, and a cost estimate (filament for the whole print at the price of the spool or type, electricity used so far, and their sum). The spool in use is listed below. Without a print the card keeps the "no print active" message and the loaded filament.
- The panel refreshes every 10 seconds while a print is running (30 seconds otherwise) and no longer redraws while you type in a field.

## [0.5.0-beta.5] - 2026-10-25

### Changed

- Edit, Delete and Restore in the spool lists are icon buttons (pencil, trash, restore) with a tooltip and an accessible name instead of text buttons. The buttons inside the edit popup stay text buttons.

## [0.5.0-beta.4] - 2026-10-25

### Fixed

- Spools in stock can be edited again, including untagged Bambu Lab spools (catalog entries and spools added with a quantity). Only an untagged Bambu Lab spool that sits in a slot keeps just the Delete button, because its values come from the RFID tag once it is detected.

## [0.5.0-beta.3] - 2026-10-25

### Changed

- Spools are no longer archived by hand: they are archived automatically when they run empty and can be restored from the archive. The Archive button is gone from the edit popup.
- Untagged Bambu Lab spools (catalog entries and spools added with a quantity) can be deleted from their row, e.g. a duplicate that was added by mistake; their values still cannot be edited until the AMS detects the spool. Editing rules for tagged Bambu Lab spools and for other brands are unchanged.

## [0.5.0-beta.2] - 2026-10-25

### Added

- Filter in the Spools card: search in name, material, brand, notes and color, and filter by material, brand and status (in stock, in a slot, low stock). The table and its totals show only the matching spools; the popup of a type still lists all its spools. A counter ("3 of 8 spools") and a reset button show while a filter is active.

### Changed

- Spools are edited with an "Edit" button on their own row (the sub-row of an expanded type, or the row of a single-spool type). Bambu Lab spools can only be edited once their RFID tag was detected; spools of other brands can always be edited. The edit popup now also has Delete.

### Removed

- The "Add stock" button and its popup, including the websocket command `druck_assistant/spool_add_stock`. Buy a pack with "Add spool" and its quantity field instead (catalog picker included).

## [0.5.0-beta.1] - 2026-10-25

### Added

- Bambu Lab catalog in the add spool form: pick a filament (e.g. "Bambu PETG Basic") and a color (German names in a German UI) to fill in name, material, brand and color; the color name and code go into the notes. Every field can still be changed. The form works without the catalog.
- The catalog of Bambu Lab spool filaments with their colors (42 filaments, 269 colors, taken from the US store on 2026-10-25) as `custom_components/druck_assistant/data/bambu_filaments.json` and a readable list in `docs/bambu-filaments.md`. Hex values, German color names and filament ids come from Bambu Studio's `filaments_color_codes.json`, matched by color code.
- Websocket command `druck_assistant/catalog` for the panel.

## [0.4.0-beta.11] - 2026-10-25

### Changed

- The "Slots" card moved from the Filament tab to a new "AMS" tab of the panel (the slot assignment and its hint are unchanged); the READMEs point to the new tab.

## [0.4.0-beta.10] - 2026-10-25

### Added

- The add and edit spool forms suggest names, materials and brands that are already captured (and common materials such as PLA or PETG) in a pick list; typing a new value still works. Picking a known name when adding a spool fills material, brand, color, price and weight from the newest spool of that name, without overwriting fields you already changed.

### Fixed

- Editing a spool whose color has an alpha channel (e.g. a color taken from the tray) no longer resets the color to black.

## [0.4.0-beta.9] - 2026-10-25

### Added

- "In stock" badge on spools that are in no slot, in the expanded spool list, in the type popup and on the row of a type with a single spool, so unused spools are easy to spot.

## [0.4.0-beta.8] - 2026-10-25

### Added

- A type with more than one spool can be expanded: click its name (the arrow shows the state) to list the single spools below the row with their stock, price, slot and RFID badge. A type with one spool is not clickable.

## [0.4.0-beta.7] - 2026-10-25

### Changed

- The filament name in the inventory is no longer clickable; the popup opens with the "Add stock" button only.
- All forms are popups over the list: adding a spool, editing a spool and adding stock. Editing a spool from the type popup shows the form on top and returns to the type popup after saving or cancelling.

## [0.4.0-beta.6] - 2026-10-25

### Fixed

- The inventory no longer merges different colors of the same filament (e.g. "Bambu PETG Basic" black and gray): a row is a name, material and color, so each color has its own total stock and average price. The alpha channel of the tray color is ignored. The color is shown as a dot, in the row tooltip and in the popup.
- Spare numbering ("#1", "#2", ...) restarts per color.

## [0.4.0-beta.5] - 2026-10-25

### Changed

- The spool list in the Filament tab is now an inventory by type: spools with the same name (ignoring " #n") and material form one row with the total stock of all of them (e.g. "2,500 / 3,000 g") and the average price per kg of the purchases, weighted by spool size. The slot column and the per-row Edit, Archive and Delete buttons are gone.
- "Add stock" opens a popup for the type with the purchase form (quantity and price) and the list of individual spools of that type, where each spool can still be edited, archived or deleted.

## [0.4.0-beta.4] - 2026-10-25

### Added

- Click a spool in the inventory (its name, or "Add stock") to add stock of that type: enter the purchased quantity and the price per kg. Full, untagged copies are created (numbered after existing ones) and matched when a new spool is detected. The price applies to the new spools only, so older spools keep what they cost.
- The Spools card shows a stock summary ("In stock: PETG Basic × 3") of all spools that are in no slot.

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

[Unreleased]: https://github.com/weskona/3D-Print-Assistant/compare/v0.7.0-beta.1...HEAD
[0.7.0-beta.1]: https://github.com/weskona/3D-Print-Assistant/compare/v0.6.0-beta.2...v0.7.0-beta.1
[0.6.0-beta.2]: https://github.com/weskona/3D-Print-Assistant/compare/v0.6.0-beta.1...v0.6.0-beta.2
[0.6.0-beta.1]: https://github.com/weskona/3D-Print-Assistant/compare/v0.5.0-beta.7...v0.6.0-beta.1
[0.5.0-beta.7]: https://github.com/weskona/3D-Print-Assistant/compare/v0.5.0-beta.6...v0.5.0-beta.7
[0.5.0-beta.6]: https://github.com/weskona/3D-Print-Assistant/compare/v0.5.0-beta.5...v0.5.0-beta.6
[0.5.0-beta.5]: https://github.com/weskona/3D-Print-Assistant/compare/v0.5.0-beta.4...v0.5.0-beta.5
[0.5.0-beta.4]: https://github.com/weskona/3D-Print-Assistant/compare/v0.5.0-beta.3...v0.5.0-beta.4
[0.5.0-beta.3]: https://github.com/weskona/3D-Print-Assistant/compare/v0.5.0-beta.2...v0.5.0-beta.3
[0.5.0-beta.2]: https://github.com/weskona/3D-Print-Assistant/compare/v0.5.0-beta.1...v0.5.0-beta.2
[0.5.0-beta.1]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.11...v0.5.0-beta.1
[0.4.0-beta.11]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.10...v0.4.0-beta.11
[0.4.0-beta.10]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.9...v0.4.0-beta.10
[0.4.0-beta.9]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.8...v0.4.0-beta.9
[0.4.0-beta.8]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.7...v0.4.0-beta.8
[0.4.0-beta.7]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.6...v0.4.0-beta.7
[0.4.0-beta.6]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.5...v0.4.0-beta.6
[0.4.0-beta.5]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.4...v0.4.0-beta.5
[0.4.0-beta.4]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.3...v0.4.0-beta.4
[0.4.0-beta.3]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.2...v0.4.0-beta.3
[0.4.0-beta.2]: https://github.com/weskona/3D-Print-Assistant/compare/v0.4.0-beta.1...v0.4.0-beta.2
[0.4.0-beta.1]: https://github.com/weskona/3D-Print-Assistant/compare/v0.3.0-beta.1...v0.4.0-beta.1
[0.3.0-beta.1]: https://github.com/weskona/3D-Print-Assistant/compare/v0.2.0...v0.3.0-beta.1
[0.2.0]: https://github.com/weskona/3D-Print-Assistant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/weskona/3D-Print-Assistant/releases/tag/v0.1.0
