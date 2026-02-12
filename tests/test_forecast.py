from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.forecast import run_forecast


def test_forecast_outputs_non_negative(tmp_path: Path):
    rows = []
    for month in pd.date_range("2025-01-01", periods=8, freq="MS"):
        rows.append(
            {
                "date": month,
                "branch_id": "S1",
                "branch_name": "Centro",
                "ingredient": "Tomate",
                "qty_ordered": 10 + month.month,
                "total_purchase_cost": 200 + month.month * 2,
            }
        )
    inventory = pd.DataFrame(rows)

    settings = {
        "paths": {
            "outputs_tables": str(tmp_path / "tables"),
            "outputs_models": str(tmp_path / "models"),
        }
    }

    class DummyLogger:
        def info(self, *args, **kwargs): ...
        def warning(self, *args, **kwargs): ...

    outputs = run_forecast(
        {"inventory": inventory},
        settings=settings,
        horizon=6,
        top_ingredients=1,
        tracker=None,
        logger=DummyLogger(),
    )
    forecast = outputs["forecast_monthly_demand"]
    assert len(forecast) == 6
    assert (forecast["forecast_qty"] >= 0).all()
