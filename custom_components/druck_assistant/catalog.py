"""Filament catalog: Bambu Lab plus third-party manufacturers (Home Assistant independent)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"
CATALOG_FILES = ("bambu_filaments.json", "third_party_filaments.json")


def load_catalog(data_dir: Path = DATA_DIR) -> dict[str, Any]:
    """Merge the catalog files into one product list."""
    products: list[dict[str, Any]] = []
    for name in CATALOG_FILES:
        products += json.loads((data_dir / name).read_text(encoding="utf-8"))["products"]
    return {"products": products}


def color_index(catalog: dict[str, Any]) -> dict[str, list[tuple[str, str]]]:
    """Colors of the catalog products that carry a color code: product name (lower case) -> [(hex, "Name (code)")]."""
    index: dict[str, list[tuple[str, str]]] = {}
    for product in catalog.get("products", []):
        for color in product.get("colors", []):
            if color.get("code") and color.get("hex"):
                index.setdefault(product["name"].lower(), []).append(
                    (color["hex"][:7].lower(), f"{color['name']} ({color['code']})")
                )
    return index


def color_note(index: dict[str, list[tuple[str, str]]], product: str, color: str) -> str:
    """"Name (code)" of the catalog color with exactly this hex value in this product, else an empty string."""
    wanted = (color or "")[:7].lower()
    found = {label for hex_, label in index.get(product.strip().lower(), []) if hex_ == wanted}
    return found.pop() if len(found) == 1 else ""
