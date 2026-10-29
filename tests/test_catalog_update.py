"""Catalog update: Bambu Studio colors and SpoolmanDB files become catalog products."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PKG = Path(__file__).parent.parent / "custom_components" / "druck_assistant"
spec = importlib.util.spec_from_file_location("catalog_update", PKG / "catalog_update.py")
cu = importlib.util.module_from_spec(spec)
sys.modules["catalog_update"] = cu
spec.loader.exec_module(cu)


def _studio(n=120, extra=None):
    rows = [
        {
            "fila_color_code": f"1{i:04d}",
            "fila_id": "GFA00",
            "fila_type": "PLA Basic",
            "fila_color_name": {"en": f"Color {i}", "de": f"Farbe {i}"},
            "fila_color": [f"#{i % 256:02X}0000FF"],
        }
        for i in range(n)
    ]
    return {"data": rows + (extra or [])}


def test_parse_studio_groups_colors_by_product():
    extra = [
        {"fila_color_code": "16100", "fila_id": "GFA03", "fila_type": "PLA Lite", "fila_color_name": {"en": "Black"}, "fila_color": ["#000000FF"]},
        {"fila_color_code": "99999", "fila_id": "GFS05", "fila_type": "Support for PLA", "fila_color_name": {"en": "White", "de": "White"}, "fila_color": ["#FFFFFFFF", "#000000FF"]},
        {"fila_color_code": "", "fila_type": "Broken", "fila_color_name": {"en": "x"}, "fila_color": ["#000000FF"]},  # skipped
    ]
    products = {p["name"]: p for p in cu.parse_studio(_studio(extra=extra))}
    assert set(products) == {"Bambu PLA Basic", "Bambu PLA Lite", "Bambu Support for PLA"}
    basic = products["Bambu PLA Basic"]
    assert basic["material"] == "PLA" and basic["filament_ids"] == ["GFA00"] and len(basic["colors"]) == 120
    assert basic["colors"][1] == {"name": "Color 1", "code": "10001", "hex": "#010000", "name_de": "Farbe 1"}
    support = products["Bambu Support for PLA"]
    assert support["material"] == "Support"
    assert support["colors"][0]["hexes"] == ["#FFFFFF", "#000000"] and "name_de" not in support["colors"][0]


def test_parse_studio_rejects_an_unexpected_file():
    for raw in ({}, {"data": []}, {"data": [{"x": 1}] * 150}, [], {"data": "no"}):
        with pytest.raises(cu.CatalogError):
            cu.parse_studio(raw)


def test_merge_keeps_the_bundled_data_and_adds_what_studio_knows_more():
    bundled = [
        {"name": "Bambu PLA Basic", "product": "PLA Basic", "material": "PLA", "brand": "Bambu Lab", "url": "https://shop/pla",
         "filament_ids": ["GFA00"], "colors": [{"name": "Jade White", "code": "10100", "hex": "#FFFFFF"}]},
        {"name": "Bambu PLA Basic Gradient", "product": "x", "material": "PLA", "brand": "Bambu Lab", "colors": []},
    ]
    studio = [
        {"name": "Bambu PLA Basic", "product": "PLA Basic", "material": "PLA", "brand": "Bambu Lab", "filament_ids": ["GFA00", "GFA09"],
         "colors": [{"name": "White", "code": "10100", "hex": "#EEEEEE", "name_de": "Weiß"}, {"name": "New", "code": "10999", "hex": "#123456"}]},
        {"name": "Bambu PLA Lite", "product": "PLA Lite", "material": "PLA", "brand": "Bambu Lab", "filament_ids": ["GFA03"],
         "colors": [{"name": "Black", "code": "16100", "hex": "#000000"}]},
    ]
    merged = {p["name"]: p for p in cu.merge_bambu(bundled, studio)}
    basic = merged["Bambu PLA Basic"]
    assert basic["url"] == "https://shop/pla" and basic["filament_ids"] == ["GFA00", "GFA09"]
    assert [c["code"] for c in basic["colors"]] == ["10100", "10999"]
    assert basic["colors"][0]["name"] == "Jade White" and basic["colors"][0]["hex"] == "#FFFFFF"  # bundled spelling stays
    assert basic["colors"][0]["name_de"] == "Weiß"  # a missing German name is filled in
    assert "Bambu PLA Basic Gradient" in merged and merged["Bambu PLA Lite"]["colors"][0]["code"] == "16100"
    assert bundled[0]["colors"] == [{"name": "Jade White", "code": "10100", "hex": "#FFFFFF"}]  # the input is untouched


def test_third_party_products_are_built_from_the_spoolmandb_files():
    files = {
        "elegoo": {"filaments": [
            {"name": "Rapid {color_name}", "material": "PLA", "weights": [{"weight": 1000, "spool_weight": 150}],
             "colors": [{"name": "Red", "hex": "ff0000"}, {"name": "Red", "hex": "ee0000"}, {"name": "Blue", "hexes": ["0000ff", "00ff00"]}]},
        ]},
    }
    products = cu.build_third_party(files)
    assert len(products) == 1
    p = products[0]
    assert (p["name"], p["material"], p["brand"], p["spool_weight_g"]) == ("Elegoo PLA Rapid", "PLA", "Elegoo", 150)
    assert [c["name"] for c in p["colors"]] == ["Red", "Blue"]  # a repeated name is dropped
    assert p["colors"][1] == {"name": "Blue", "hex": "#0000FF", "hexes": ["#0000FF", "#00FF00"]}
    with pytest.raises(cu.CatalogError):
        cu.build_third_party({"elegoo": {"nothing": 1}})
    with pytest.raises(cu.CatalogError):
        cu.build_third_party({})
