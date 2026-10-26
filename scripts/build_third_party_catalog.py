#!/usr/bin/env python3
"""Build data/third_party_filaments.json and docs/third-party-filaments.md from SpoolmanDB.

Usage: build_third_party_catalog.py <SpoolmanDB filaments dir> <commit> <retrieved date>

SpoolmanDB (https://github.com/Donkie/SpoolmanDB, MIT license) lists filaments of many
manufacturers with color names and hex values. Only the manufacturers in BRANDS are used.
"""

import json
import re
import sys
from pathlib import Path

BRANDS = {  # file name -> display name
    "anycubic": "Anycubic",
    "elegoo": "Elegoo",
    "sunlu": "Sunlu",
    "creality": "Creality",
    "esun": "eSUN",
    "polymaker": "Polymaker",
    "prusament": "Prusament",
    "overture": "Overture",
    "flashforge": "Flashforge",
}
ROOT = Path(__file__).resolve().parent.parent


def product_name(brand: str, material: str, name: str) -> str:
    base = re.sub(r"\s+", " ", name.replace("{color_name}", " ")).strip(" -")
    if not base:
        return f"{brand} {material}"
    if material.lower() in base.lower():
        return f"{brand} {base}"
    return f"{brand} {material} {base}"


def hex_of(color: dict) -> str | None:
    value = color.get("hex") or (color.get("hexes") or [None])[0]
    return "#" + value.lstrip("#").upper()[:6] if value else None


def main(src: Path, commit: str, retrieved: str) -> None:
    products: dict[tuple[str, str], dict] = {}
    for key, brand in BRANDS.items():
        for item in json.loads((src / f"{key}.json").read_text(encoding="utf-8"))["filaments"]:
            name = product_name(brand, item["material"], item["name"])
            product = products.setdefault(
                (name, item["material"]),
                {
                    "name": name,
                    "product": name.removeprefix(brand).strip(),
                    "material": item["material"],
                    "brand": brand,
                    "weight_g": (item.get("weights") or [{}])[0].get("weight", 1000),
                    "spool_weight_g": (item.get("weights") or [{}])[0].get("spool_weight"),
                    "colors": [],
                },
            )
            seen = {c["name"].lower() for c in product["colors"]}
            for color in item.get("colors", []):
                hexes = ["#" + h.lstrip("#").upper()[:6] for h in color.get("hexes", [])]
                entry = {"name": color["name"].strip(), "hex": hex_of(color)}
                if len(hexes) > 1:
                    entry["hexes"] = hexes
                if entry["hex"] and entry["name"].lower() not in seen:
                    seen.add(entry["name"].lower())
                    product["colors"].append(entry)
    result = sorted(
        (p for p in products.values() if p["colors"]),
        key=lambda p: (p["brand"].lower(), p["name"].lower()),
    )
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
