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
