from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from src.utils.paths import CONFIG_DIR


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")
    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file) or {}
    if not isinstance(content, dict):
        raise ValueError(f"El archivo {path} no contiene un diccionario YAML válido.")
    return content


def deep_update(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = deep_update(base[key], value)
        else:
            base[key] = value
    return base


def load_settings(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = load_yaml(CONFIG_DIR / "settings.yml")
    if overrides:
        settings = deep_update(settings, overrides)

    # Bandera opcional: POLARS=1
    env_polars = os.getenv("POLARS", "").strip().lower()
    if env_polars in {"1", "true", "yes", "si", "sí"}:
        settings.setdefault("runtime", {})
        settings["runtime"]["use_polars"] = True

    return settings


def load_schema_map() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "schema_map.yml")


def load_recipe_map() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "recipe_map.yml")
