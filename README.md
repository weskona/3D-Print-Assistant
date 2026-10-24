# 3D-Druck-Assistant

Home-Assistant-Integration für Bambu-Lab-Drucker. Sie setzt auf
[ha-bambulab](https://github.com/greghesp/ha-bambulab) auf und liest dessen Entitäten
(Druckstatus, Gewicht, aktives Filament), statt selbst mit dem Drucker zu sprechen.

## Funktionen

- Druckhistorie (letzte 200 Drucke, persistent) mit Dauer, Ergebnis, Gewicht, Material und Farbe
- Filamentverbrauch und -kosten pro Druck und gesamt
- Stromkosten pro Druck über einen Energiezähler (kWh) oder einen Leistungssensor (W, wird über die Druckdauer integriert); Strompreis fest oder aus einer Entität
- Ereignisse für Automationen: `druck_assistant_print_started`, `druck_assistant_print_finished`,
  `druck_assistant_print_failed`, `druck_assistant_filament_low`

## Installation

1. ha-bambulab installieren und den Drucker einrichten.
2. `custom_components/druck_assistant` nach `config/custom_components/` kopieren (oder per HACS als Custom Repository).
3. Home Assistant neu starten, Integration „3D-Druck-Assistant“ hinzufügen und den Drucker wählen.
4. In den Optionen Filamentpreis pro kg und Warnschwelle einstellen.

## Release

Bei jedem Push auf `main` prüft der Workflow `.github/workflows/release.yml` die Version in
`custom_components/druck_assistant/manifest.json`. Gibt es für `v<version>` noch keinen Tag,
wird er angelegt und ein GitHub Release mit `druck_assistant.zip` erstellt. Die Release Notes
stammen aus dem passenden Abschnitt `## [<version>]` der `CHANGELOG.md`, sonst werden sie
automatisch erzeugt. Zum Veröffentlichen also Version im Manifest erhöhen und den
`[Unreleased]`-Abschnitt in `## [<version>] - <Datum>` umbenennen.
