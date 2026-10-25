# 3D Print Assistant

[English](README.md)

> **Beta:** Dieses Projekt befindet sich im Beta-Status. Änderungen sind möglich, bitte melde Probleme als Issue.

Home-Assistant-Integration für Bambu-Lab-Drucker. Sie setzt auf
[ha-bambulab](https://github.com/greghesp/ha-bambulab) auf und liest dessen Entitäten
(Druckstatus, Gewicht, aktives Filament), statt selbst mit dem Drucker zu sprechen.

## Funktionen

- Druckhistorie (letzte 200 Drucke, persistent) mit Dauer, Ergebnis, Gewicht, Material und Farbe
- Filamentverbrauch und -kosten pro Druck und gesamt
- Stromkosten pro Druck über einen Energiezähler (kWh) oder einen Leistungssensor (W, wird über die Druckdauer integriert); Strompreis fest oder aus einer Entität
- Filamentverwaltung: Spulenbestand mit Restgewicht, Preis und Farbe, zugeordnet zu AMS-/Externe-Spule-Slots; nach jedem Druck wird das verbrauchte Filament abgezogen, bei niedrigem Bestand gibt es ein Ereignis
- Eigenes Panel „3D Print Assistant“ in der Seitenleiste mit Kennzahlen, aktuellem Druck/Filament und Druckhistorie (aktualisiert sich live bei Druckstart und -ende)
- Ereignisse für Automationen: `druck_assistant_print_started`, `druck_assistant_print_finished`,
  `druck_assistant_print_failed`, `druck_assistant_filament_low`

## Filamentverwaltung

Im Tab „Filament“ des Panels (Bearbeiten nur für Administratoren) legst du Spulen an und ordnest
sie den Slots des Druckers zu. Verwendet wird der Slot, der beim Druckstart aktiv ist: Der Preis
seiner Spule ersetzt den Sortenpreis, das verbrauchte Gewicht wird am Druckende abgezogen.
Mit „Aus AMS importieren“ werden aus den belegten AMS-Slots Spulen angelegt. Neue Bambu-Spulen mit
RFID-Tag werden zusätzlich automatisch übernommen (Option „Neue Bambu-Spulen automatisch übernehmen“);
Spulen ohne Tag, etwa Fremdfilament oder die externe Spule, werden nur über den Button importiert.
Der Restbestand wird aus der AMS-Prozentanzeige geschätzt und lässt sich von Hand korrigieren.
**Bestand an einer erkannten Spule hinzufügen:** Die Liste zeigt eine Zeile pro Sorte (z. B. „Bambu PETG Basic Black“)
mit dem Gesamtbestand aller Spulen und dem Durchschnittspreis pro kg. Klicke eine Zeile oder „Bestand hinzufügen“, um ein Popup
zu öffnen, und gib die gekaufte Anzahl und den Preis pro kg ein. Das Popup listet auch die einzelnen Spulen der Sorte, die du dort bearbeiten, archivieren oder löschen kannst. Die neuen Spulen werden voll angelegt und zum Bestand der Sorte gezählt; sie werden aufgebraucht, sobald neue Spulen erkannt werden. Nur die neuen Spulen
bekommen den eingegebenen Preis, vorhandene behalten ihren.

**Großeinkauf:** Lege das Paket mit dem Feld „Anzahl“ an (z. B. 4 x „PETG Basic Schwarz“, Farbe Schwarz).
Wird eine neue Bambu-Spule erkannt, sucht die Integration zuerst eine passende Spule im Bestand
(nicht in einem Slot, noch ohne Tag, gleiche Sorte, ähnliche Farbe) und verwendet sie, statt eine neue
anzulegen. Der Bestand sinkt von 4 auf 3, und die eingelegte Spule wird ab dann verfolgt. Ohne Treffer wird eine neue Spule angelegt.
Passt die Zuordnung nicht, wähle in der Slot-Liste des Tabs „Filament“ die richtige Spule: Der RFID-Tag
wandert zu ihr, und die Korrektur bleibt bestehen. „keine“ stoppt die automatische Zuordnung für die
Spule, die gerade im Slot steckt (der Button „Aus AMS importieren“ hebt das wieder auf). Den RFID-Tag
einer Spule kannst du auch im Formular ändern oder leeren. Eine Bestandsspule, die ihren Tag verloren hat, bleibt einfach im Bestand.

Erreicht der Restbestand einer Spule nach einem Druck 0 g, kommt sie automatisch ins Archiv
(Option „Leere Spulen automatisch archivieren“) und löst `druck_assistant_spool_empty` aus. Du kannst
Spulen auch von Hand archivieren und in der einklappbaren Liste „Archivierte Spulen“ wiederherstellen.
Archivierte Spulen werden nicht automatisch wieder importiert oder zugeordnet, auch wenn sie noch im AMS stecken.
Bei Drucken mit mehreren Spulen wird alles der beim Start aktiven Spule zugerechnet.

## Installation

1. ha-bambulab installieren und den Drucker einrichten.
2. `custom_components/druck_assistant` nach `config/custom_components/` kopieren (oder per HACS als Custom Repository).
3. Home Assistant neu starten, Integration „3D Print Assistant“ hinzufügen und den Drucker wählen.
4. In den Optionen Filamentpreis pro kg und Warnschwelle einstellen.

## Release

Bei jedem Push auf `main` prüft der Workflow `.github/workflows/release.yml` die Version in
`custom_components/druck_assistant/manifest.json`. Gibt es für `v<version>` noch keinen Tag,
wird er angelegt und ein GitHub Release mit `druck_assistant.zip` erstellt. Die Release Notes
stammen aus dem passenden Abschnitt `## [<version>]` der `CHANGELOG.md`, sonst werden sie
automatisch erzeugt. Zum Veröffentlichen also Version im Manifest erhöhen und den
`[Unreleased]`-Abschnitt in `## [<version>] - <Datum>` umbenennen.

## Sprachen

Die Quellsprache ist Englisch. Das deutsche Sprachpaket (`translations/de.json` und das Panel) wird
automatisch anhand der Home-Assistant-Sprache gewählt.
