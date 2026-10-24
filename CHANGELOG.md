# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
und dieses Projekt hält sich an [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Added

- Initiales Projekt-Setup mit README.
- Changelog im Format von Keep a Changelog.
- Home-Assistant-Integration `druck_assistant` auf Basis von ha-bambulab: Druckhistorie, Filamentverbrauch und -kosten, Sensoren sowie Ereignisse für Druckstart, -ende, -fehler und niedriges Filament.
- Stromkosten: optionaler Energiezähler (kWh) und Leistungssensor (W) im Config-Flow, Strompreis fest oder per Entität, neue Sensoren für Stromverbrauch, Stromkosten und Strompreis. Die Druckkosten enthalten nun Filament und Strom.
- Filamentpreise pro Sorte (z. B. `PLA=20`) in den Optionen, Sensor für das aktuelle Filament inklusive Preis pro kg. Kostensensoren in Euro.
- GitHub-Workflow, der nach einem Push auf `main` Tag und Release erstellt.

[Unreleased]: https://github.com/weskona/3D-Druck-Assistant/commits/main
