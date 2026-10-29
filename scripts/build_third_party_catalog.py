#!/usr/bin/env python3
"""Build data/third_party_filaments.json and docs/third-party-filaments.md from SpoolmanDB.

Usage: build_third_party_catalog.py <SpoolmanDB filaments dir> <commit> <retrieved date>

SpoolmanDB (https://github.com/Donkie/SpoolmanDB, MIT license) lists filaments of many
manufacturers with color names and hex values. Only the manufacturers in BRANDS are used.
"""

import importlib.util
import json
import sys
from pathlib import Path

# The conversion lives in the integration (it also runs there when the catalog is updated).
_spec = importlib.util.spec_from_file_location(
    "catalog_update", Path(__file__).resolve().parent.parent / "custom_components/druck_assistant/catalog_update.py"
)
catalog_update = importlib.util.module_from_spec(_spec)
sys.modules["catalog_update"] = catalog_update
_spec.loader.exec_module(catalog_update)
BRANDS = catalog_update.BRANDS
ROOT = Path(__file__).resolve().parent.parent


def main(src: Path, commit: str, retrieved: str) -> None:
    files = {key: json.loads((src / f"{key}.json").read_text(encoding="utf-8")) for key in BRANDS}
    result = catalog_update.build_third_party(files)
    data = {
        "source": "https://github.com/Donkie/SpoolmanDB",
        "license": "MIT, Copyright (c) 2024 Donkie",
        "commit": commit,
        "retrieved": retrieved,
        "note": "Community-maintained filament data of the manufacturers in scripts/build_third_party_catalog.py. Product names are built from manufacturer, material and the product line; hex values are as listed in SpoolmanDB and can be approximate.",
        "products": result,
    }
    (ROOT / "custom_components/druck_assistant/data/third_party_filaments.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Third-party filament catalog",
        "",
        f"Source: <{data['source']}> (MIT license, Copyright (c) 2024 Donkie), commit `{commit[:10]}`, retrieved {retrieved}.",
        "Community-maintained data; hex values can be approximate. Machine-readable copy: `custom_components/druck_assistant/data/third_party_filaments.json`.",
        "",
        f"{len(result)} filaments, {sum(len(p['colors']) for p in result)} colors.",
        "",
    ]
    brand = None
    for p in result:
        if p["brand"] != brand:
            brand = p["brand"]
            lines += [f"## {brand}", ""]
        lines += [f"### {p['name']}", f"Material: {p['material']} · {len(p['colors'])} colors", "", ", ".join(c["name"] for c in p["colors"]), ""]
    (ROOT / "docs/third-party-filaments.md").write_text("\n".join(lines), encoding="utf-8")
    print(len(result), "filaments", sum(len(p["colors"]) for p in result), "colors")


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2], sys.argv[3])
