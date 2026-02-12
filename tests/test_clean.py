from __future__ import annotations

import pandas as pd

from src.data.clean import clean_dataset


def test_clean_sales_basic_mapping_and_types():
    raw = pd.DataFrame(
        {
            "Ticket_ID": ["T1"],
            "Fecha": ["2025-01-01"],
            "Hora": ["13:30"],
            "Sucursal_ID": ["S1"],
            "Sucursal_Nombre": ["Centro"],
            "Platillo": ["Taco"],
            "Categoria": ["Platos Fuertes"],
            "Precio_Unitario": ["100"],
            "Cantidad": ["2"],
            "Total_Venta": ["200"],
            "Costo_Ingredientes": [None],
            "Metodo_Pago": ["Efectivo"],
        }
    )
    dataset_map = {
        "columns": {
            "ticket_id": ["Ticket_ID"],
            "date": ["Fecha"],
            "time": ["Hora"],
            "branch_id": ["Sucursal_ID"],
            "branch_name": ["Sucursal_Nombre"],
            "dish": ["Platillo"],
            "category": ["Categoria"],
            "unit_price": ["Precio_Unitario"],
            "quantity": ["Cantidad"],
            "total_sale": ["Total_Venta"],
            "ingredient_cost": ["Costo_Ingredientes"],
            "payment_method": ["Metodo_Pago"],
        }
    }

    class DummyLogger:
        def info(self, *args, **kwargs): ...
        def warning(self, *args, **kwargs): ...

    clean = clean_dataset("sales", raw, dataset_map, logger=DummyLogger())
    assert "ticket_id" in clean.columns
    assert "daypart" in clean.columns
    assert clean["total_sale"].iloc[0] == 200
    assert clean["ingredient_cost"].iloc[0] > 0


def test_clean_branches_postal_code_string_for_parquet_safety():
    raw = pd.DataFrame(
        {
            "Sucursal_ID": ["S1", "S2"],
            "Nombre_Sucursal": ["Centro", "Norte"],
            "Ciudad": ["CDMX", "Puebla"],
            "Codigo_Postal": [6600, "72000"],
            "Costos_Operativos_Total": ["100000", "120000"],
        }
    )
    dataset_map = {
        "columns": {
            "branch_id": ["Sucursal_ID"],
            "branch_name": ["Nombre_Sucursal"],
            "city": ["Ciudad"],
            "postal_code": ["Codigo_Postal"],
            "operational_cost_total": ["Costos_Operativos_Total"],
        }
    }

    class DummyLogger:
        def info(self, *args, **kwargs): ...
        def warning(self, *args, **kwargs): ...

    clean = clean_dataset("branches", raw, dataset_map, logger=DummyLogger())
    assert "postal_code" in clean.columns
    assert str(clean["postal_code"].dtype).startswith("string")
