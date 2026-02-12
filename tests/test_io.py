from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.utils.io as io_utils


def test_write_table_fallback_to_csv(monkeypatch, tmp_path: Path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    class DummyLogger:
        def warning(self, *args, **kwargs): ...
        def info(self, *args, **kwargs): ...

    monkeypatch.setattr(io_utils, "_supports_parquet", lambda: False)
    saved = io_utils.write_table(
        df,
        tmp_path / "sample",
        logger=DummyLogger(),
        allow_csv_fallback=True,
    )
    assert saved.suffix == ".csv"
    assert saved.exists()

    loaded = io_utils.read_table(tmp_path / "sample", logger=DummyLogger())
    assert len(loaded) == 2
