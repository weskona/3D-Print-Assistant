# Conventions

- All code, comments, identifiers, commit messages, docs and source strings are in English.
- German is provided as a language pack only: `custom_components/druck_assistant/translations/de.json`
  and the `de` block in `frontend/druck-assistant-panel.js` (plus `README.de.md`).
- When adding or changing a user-facing string, update `strings.json`, `translations/en.json`,
  `translations/de.json` and the panel `TRANSLATIONS` together.
- The project stays in beta: manifest versions are `0.x.y-beta.N`, never a stable version unless the user says so.
  The release workflow marks any version containing `-` as a pre-release.
- Keep `CHANGELOG.md` in Keep a Changelog format, English only.
