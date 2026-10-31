# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.10.0-beta.7] - 2026-10-31

### Added

- Event log tab: the last 200 things the assistant noticed (print started, finished or failed, a spool almost empty or used up, a spool taken over from the AMS, not enough filament for a print, low stock, a restored backup), newest first, with a button to clear it. The log is kept across restarts.
- Settings tab: download a backup file with the spools, slots, projects, settings and the print history, and restore it from a file. A restore replaces all of that (history per printer serial); the state before is kept aside in the Home Assistant storage (`druck_assistant.before_restore`).

### Fixed

- A Bambu Lab spool with an RFID tag put into a slot that held a third-party spool (e.g. Anycubic) was taken for that spool: the tag was written onto it and the slot kept showing it. A hand-entered spool is now only tagged when it is a Bambu Lab spool of the same material; otherwise the Bambu spool is created (or found in the stock) and takes the slot.
- A spool that is reassigned to a slot while a print is running is now the one charged for that slot; before, the spool assigned at the start of the print kept the filament.

## [0.10.0-beta.6] - 2026-10-30

### Fixed

- The panel jumped back to the top a few seconds after scrolling down (since 0.10.0-beta.4): the refresh rebuilt the page and read its layout half way, which reset the scroll position. The position is now put back after a rebuild, and the active tab is centred once the page is complete.

## [0.10.0-beta.5] - 2026-10-30

### Changed

- Narrow screens: the tables (filament list, archive, stock, statistics) show every row as a small block with labelled values instead of a wide table that has to be scrolled.

## [0.10.0-beta.4] - 2026-10-30

### Added

- History: a print can be renamed (pencil button on the row), e.g. when the slicer gave it a wrong name.

### Changed

- Panel layout for phones and tablets: the tabs scroll instead of overflowing (the active one is kept in view), cards and dialogs use less padding on narrow screens, history rows move the cost to its own line in a narrow card, and touch screens get larger buttons and 16px inputs (no zoom on focus in iOS).

### Fixed

- A print on a spool the printer cannot read (third-party filament) is stored with the material and colour of the assigned spool instead of "Empty" and a transparent colour.

## [0.10.0-beta.3] - 2026-10-29

### Added

- Statistics tab: a card with the five longest prints (print time, plus weight, material and cost).

## [0.10.0-beta.2] - 2026-10-29

### Changed

- Filament list: the row of a type with several spools shows the slot of the spool that is in a slot, so it is visible without expanding the group.

## [0.10.0-beta.1] - 2026-10-29

### Changed

- Version number only. The GitHub release list sorts the pre-release part as text, so `beta.9` stood above `beta.10`, `beta.11` and `beta.12` and looked like the newest release. The minor version is raised so that the newest release is listed first again; the code is that of 0.9.0-beta.12.

## [0.9.0-beta.12] - 2026-10-29

### Fixed

- A print picked up after a restart now gets the printer's start time and the energy meter reading of its start also when the progress was not yet known when the session began (the usual case right after a restart): the check is repeated on every later change (and 30 and 120 seconds after the start) until the progress and the printer's start time are known. In beta.11 the energy was still counted only from the restart on in that case.

## [0.9.0-beta.11] - 2026-10-29

### Fixed

- A print that is picked up after a restart of Home Assistant in the middle of it keeps the printer's start time (so duration and energy cover the whole print) and takes the energy meter reading of that moment from the recorder. Before, the energy was counted only from the restart on. The start time is only used once the print has reached 3 % because it can still belong to the previous job before that.

## [0.9.0-beta.10] - 2026-10-29

### Fixed

- A print whose session began before the slots were ready (right after a restart of Home Assistant) is given the spool of the active slot as soon as it is known. Before, it stayed without a spool: the print was charged at the default price per kg and its filament was taken from no spool.

## [0.9.0-beta.9] - 2026-10-29

### Fixed

- A print that is already running when Home Assistant starts (restart in the middle of a print) now gets its session: the tracker looks for it at startup and on every slot or progress change. Without a session the print was neither recorded in the history nor charged to its spool, and the panel showed the default price per kg instead of the spool's.

## [0.9.0-beta.8] - 2026-10-29

### Added

- Projects: tick prints in the history (a click on the row) to add up filament, time, electricity and cost, and add them to a project. The new Projects tab shows every project with the totals of its prints (filament per material, time, electricity, filament and electricity cost), lets you remove prints, rename and delete a project, and copy the summary as text. A print belongs to one project at most; the history row shows its project.

## [0.9.0-beta.7] - 2026-10-29

### Added

- Filament tab: the spool list can also be filtered by color (the color families of the spools, like black, gray or pink).

## [0.9.0-beta.6] - 2026-10-29

### Changed

- The weigh dialog has a dropdown with the spool types of the settings (and the brand default) next to the weight of the empty spool; picking one fills the weight and is kept for the spool.

### Fixed

- Catalog update: the downloaded files were read only in part ("Unterminated string"), so the update always failed and kept the bundled catalog. They are now read completely.

## [0.9.0-beta.5] - 2026-10-29

### Added

- The filament catalog can be updated from the Settings tab (button, or once a week when switched on): all Bambu Lab colors come from Bambu Studio's color file (new products such as PLA Lite, PLA Tough, ABS and more colors of existing ones), the other manufacturers from SpoolmanDB. The downloaded data is kept beside the bundled catalog; a failed or unexpected download leaves the old catalog in place. Spools the AMS adds afterwards get more color names in their notes.

### Changed

- `scripts/build_third_party_catalog.py` uses the same conversion as the update (`catalog_update.py`).

## [0.9.0-beta.4] - 2026-10-29

### Added

- New Settings tab: empty spool weight per brand, own spool types (e.g. a self-printed Bambu spool) that are picked in the spool form, and the thresholds for the weigh suggestion and the AMS deviation warning. A weighing only pins a spool's own tare when it differs from the default.
- Correction factor for the consumption: each weighing compares what the prints booked since the last weighing (or since the spool was new and full) with the weighed amount. From three weighings with at least 50 g of use the Statistics tab suggests a factor (real consumption / slicer weight) that can be applied or reset; it is applied to every deduction and to rebookings. After a weighing the panel shows how far the slicer was off.
- The Filament tab lists spools outside the AMS that are worth weighing (amount is an estimate, or 20 g or more used since the last weighing) with a scale button.

## [0.9.0-beta.3] - 2026-10-29

### Fixed

- Filament list: a spool that is the only one of its type now also shows the slot it sits in (like the spools in an expanded group).

## [0.9.0-beta.2] - 2026-10-29

### Changed

- Spools that the AMS adds automatically get the color name and code from the catalog in their notes ("Plum (11204)"), when the hex value matches exactly. Existing Bambu spools with empty notes are filled once at startup.
- The remaining amount of a spool is calculated by the integration; the AMS percent no longer overwrites it. A new spool starts full. When the AMS reports it as used, the spool is marked "Unweighed" until it is weighed (or its amount is edited). The AMS tab shows the calculated percent and warns when the AMS value differs by more than 15 points.
- Filament list: the "In stock" badge only marks a spool that is still full and not in a slot; a spool with an RFID tag gets the RFID badge in every row, a spool at or below 15 % a red "Almost empty" badge.
- AMS tab: the spool list of a slot shows the color (the first line of the notes, e.g. "Plum (11204)", else a color name), grams left, location and the slot a spool already sits in, so spools with the same name can be told apart; spools of the slot's material come first.
- Statistics tab: the cost per month is split into filament and electricity (two-color bar, legend and both amounts per month).

## [0.9.0-beta.1] - 2026-10-28

### Added

- Weighing: a scale button on every spool turns the weight on the scale into the filament left (minus the empty spool: 250 g for Bambu Lab, 200 g otherwise, or an own value kept per spool).
- More spool details: purchase date, shop, order number, batch, location and last drying. A label with the spool's data can be printed.
- Warning before it runs out: when a spool holds less than the running print needs from it, the Overview tab shows a warning and the event `druck_assistant_spool_insufficient` fires once; a slot that can take over is named.
- Replacement from the stock: the AMS tab and the `druck_assistant_filament_low` event (`replacement`) name the stock spool to insert for an almost empty spool.
- Minimum stock per type (new option) with a stock and shopping list in the Filament tab (missing grams, estimated cost, days the stock lasts, copy button) and the event `druck_assistant_stock_low`.
- Rebooking: a print in the history can be charged to another spool; the filament moves between the spools.
- New "Statistics" tab: per material the cost, filament, failure rate and wasted money, the cost per month, the most expensive prints and the price per kg of the purchases.
- CSV export of the spools and the history, and CSV import of spools.

## [0.8.0-beta.1] - 2026-10-28

### Changed

- The filament of a print is split over the spools it really used. The add-on follows the active slot during the print and takes the grams per slot from the slicer when ha-bambulab reports them. When a spool runs empty and the AMS continues with another spool, the first spool is charged only what was left on it and the rest goes to the other spool (or, without enough data, the remaining percent of the AMS per slot decides). Every spool is charged with its own price, and the print history lists the spools of a multi spool print.
- A print that did not finish now counts only for the progress it reached; before, the full weight was deducted.
- History records have a new `usages` list (spools of a multi spool print) and `planned_g` (the weight of the whole print as sliced).

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
