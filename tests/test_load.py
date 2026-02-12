from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.data.load import _select_best_xlsx, load_raw_datasets


def test_load_raw_datasets_from_json(tmp_path: Path):
    raw_json = tmp_path / "json"
    raw_csv = tmp_path / "csv"
    raw_xlsx = tmp_path / "xlsx"
    raw_json.mkdir()
    raw_csv.mkdir()
    raw_xlsx.mkdir()

    payloads = {
        "ventascsv.json": [
            {
                "Ticket_ID": "T1",
                "Fecha": "2025-01-01",
                "Sucursal_ID": "S1",
                "Platillo": "Taco",
                "Cantidad": 1,
                "Total_Venta": 100,
            }
        ],
        "clientes.json": [
            {
                "Cliente_ID": "C1",
                "Fecha_Registro": "2025-01-01",
                "Visitas_Ultimo_Año": 2,
                "Gasto_Promedio": 150,
            }
        ],
        "sucursales.json": [
            {
                "Sucursal_ID": "S1",
                "Nombre_Sucursal": "CDMX",
                "Ciudad": "CDMX",
                "Costos_Operativos_Total": 10000,
            }
        ],
        "inventarios.json": [
            {
                "Registro_ID": "I1",
                "Fecha": "2025-01-01",
                "Sucursal_ID": "S1",
                "Ingrediente": "Tomate",
                "Cantidad_Pedida": 10,
                "Costo_Total_Compra": 200,
            }
        ],
        "canales_digitales.json": [
            {
                "Registro_ID": "D1",
                "Fecha": "2025-01-01",
                "Sucursal_ID": "S1",
                "Plataforma": "Instagram",
                "Sentimiento": "Positivo",
            }
        ],
    }
    for file_name, content in payloads.items():
        (raw_json / file_name).write_text(
            json.dumps(content, ensure_ascii=False), encoding="utf-8"
        )

    settings = {
        "runtime": {"use_polars": False},
        "paths": {
            "raw_json": str(raw_json),
            "raw_csv": str(raw_csv),
            "raw_xlsx": str(raw_xlsx),
        },
    }

    class DummyLogger:
        def info(self, *args, **kwargs): ...
        def warning(self, *args, **kwargs): ...

    tables, report = load_raw_datasets(settings=settings, logger=DummyLogger())
    assert set(tables.keys()) == {
        "sales",
        "customers",
        "branches",
        "inventory",
        "digital",
    }
    assert report["sales"]["source"] == "json"
    assert len(tables["sales"]) == 1


def test_xlsx_selection_deduplicates_workbooks(tmp_path: Path):
    xlsx_dir = tmp_path / "xlsx"
    xlsx_dir.mkdir()

    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    file_a = xlsx_dir / "a.xlsx"
    file_b = xlsx_dir / "b.xlsx"

    for fp in [file_a, file_b]:
        with pd.ExcelWriter(fp) as writer:
            df.to_excel(writer, sheet_name="Ventas", index=False)

    class DummyLogger:
        def info(self, *args, **kwargs): ...
        def warning(self, *args, **kwargs): ...

    selected_df, meta = _select_best_xlsx(
        [file_a, file_b], "Ventas", logger=DummyLogger()
    )
    assert selected_df is not None
    assert len(selected_df) == 2
    assert meta["duplicates_found"] >= 1
