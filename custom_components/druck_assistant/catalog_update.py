"""Turn the upstream filament data into catalog products (Home Assistant independent).

Two sources keep the catalog current without a new release of the integration:

* Bambu Studio's filaments_color_codes.json: every Bambu Lab filament color with its code,
  filament id, names in many languages and hex values.
* SpoolmanDB (MIT): community data of the other manufacturers (BRANDS).
"""

from __future__ import annotations

import re
from typing import Any

STUDIO_URL = (
    "https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/filament/"
    "filaments_color_codes.json"
)
SPOOLMANDB_URL = "https://raw.githubusercontent.com/Donkie/SpoolmanDB/main/filaments/{key}.json"

BRANDS = {  # SpoolmanDB file name -> display name
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

MIN_STUDIO_COLORS = 100  # a smaller file is not the file we expect
MIN_BRAND_PRODUCTS = 1


class CatalogError(ValueError):
    """The downloaded data does not look like the expected file."""


def _hex(value: Any) -> str | None:
    text = str(value or "").lstrip("#")
    return "#" + text.upper()[:6] if re.fullmatch(r"[0-9a-fA-F]{6,8}", text) else None


def material_of(fila_type: str) -> str:
    """"PLA Basic" -> PLA, "PETG-CF" -> PETG-CF, "Support for PLA" -> Support."""
    if fila_type.lower().startswith("support"):
        return "Support"
    return fila_type.split()[0] if fila_type else ""


def parse_studio(raw: Any) -> list[dict[str, Any]]:
    """Bambu products with their colors from Bambu Studio's filaments_color_codes.json."""
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or len(rows) < MIN_STUDIO_COLORS:
        raise CatalogError("unexpected Bambu Studio color file")
    products: dict[str, dict[str, Any]] = {}
    for row in rows:
        try:
            fila_type, code, names = str(row["fila_type"]).strip(), str(row["fila_color_code"]), row["fila_color_name"]
            hexes = [h for h in (_hex(x) for x in row.get("fila_color") or []) if h]
            name_en = str(names.get("en") or "").strip()
        except (KeyError, AttributeError, TypeError) as err:
            raise CatalogError("unexpected Bambu Studio color file") from err
        if not fila_type or not code or not name_en or not hexes:
            continue
        product = products.setdefault(
            f"Bambu {fila_type}",
            {
                "name": f"Bambu {fila_type}",
                "product": fila_type,
                "material": material_of(fila_type),
                "brand": "Bambu Lab",
                "filament_ids": [],
                "colors": [],
            },
        )
        if row.get("fila_id") and row["fila_id"] not in product["filament_ids"]:
            product["filament_ids"].append(row["fila_id"])
        color: dict[str, Any] = {"name": name_en, "code": code, "hex": hexes[0]}
        if names.get("de") and names["de"] != name_en:
            color["name_de"] = str(names["de"]).strip()
        if len(hexes) > 1:
            color["hexes"] = hexes
        product["colors"].append(color)
    return list(products.values())


def merge_bambu(bundled: list[dict[str, Any]], studio: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The bundled Bambu products plus what Bambu Studio knows more.

    A product with the same name gets the colors it lacks (by color code) and missing German
    names; the bundled data keeps its links and its own spelling. New products are added.
    """
    merged = [{**p, "colors": [dict(c) for c in p.get("colors", [])]} for p in bundled]
    by_name = {p["name"]: p for p in merged}
    for new in studio:
        product = by_name.get(new["name"])
        if product is None:
            by_name[new["name"]] = product = {**new, "colors": []}
            merged.append(product)
        known = {c.get("code"): c for c in product["colors"] if c.get("code")}
        for color in new["colors"]:
            have = known.get(color["code"])
            if have is None:
                product["colors"].append(dict(color))
            else:
                for key in ("name_de", "hexes"):
                    if key in color and key not in have:
                        have[key] = color[key]
        for fid in new.get("filament_ids", []):
            if fid not in product.setdefault("filament_ids", []):
                product["filament_ids"].append(fid)
    return merged


def product_name(brand: str, material: str, name: str) -> str:
    base = re.sub(r"\s+", " ", name.replace("{color_name}", " ")).strip(" -")
    if not base:
        return f"{brand} {material}"
    if material.lower() in base.lower():
        return f"{brand} {base}"
    return f"{brand} {material} {base}"


def build_third_party(files: dict[str, Any]) -> list[dict[str, Any]]:
    """Products of the other manufacturers; files maps the SpoolmanDB file name to its parsed JSON."""
    products: dict[tuple[str, str], dict[str, Any]] = {}
    for key, brand in BRANDS.items():
        data = files.get(key)
        if data is None:
            continue
        items = data.get("filaments") if isinstance(data, dict) else None
        if not isinstance(items, list):
            raise CatalogError(f"unexpected SpoolmanDB file for {brand}")
        for item in items:
            try:
                name = product_name(brand, item["material"], item["name"])
                weight = (item.get("weights") or [{}])[0]
                product = products.setdefault(
                    (name, item["material"]),
                    {
                        "name": name,
                        "product": name.removeprefix(brand).strip(),
                        "material": item["material"],
                        "brand": brand,
                        "weight_g": weight.get("weight", 1000),
                        "spool_weight_g": weight.get("spool_weight"),
                        "colors": [],
                    },
                )
                seen = {c["name"].lower() for c in product["colors"]}
                for color in item.get("colors", []):
                    hexes = [h for h in (_hex(x) for x in color.get("hexes", [])) if h]
                    entry: dict[str, Any] = {
                        "name": color["name"].strip(),
                        "hex": _hex(color.get("hex")) or (hexes[0] if hexes else None),
                    }
                    if len(hexes) > 1:
                        entry["hexes"] = hexes
                    if entry["hex"] and entry["name"].lower() not in seen:
                        seen.add(entry["name"].lower())
                        product["colors"].append(entry)
            except (KeyError, AttributeError, TypeError) as err:
                raise CatalogError(f"unexpected SpoolmanDB file for {brand}") from err
    result = sorted((p for p in products.values() if p["colors"]), key=lambda p: (p["brand"].lower(), p["name"].lower()))
    if len(result) < MIN_BRAND_PRODUCTS:
        raise CatalogError("no third-party products found")
    return result
