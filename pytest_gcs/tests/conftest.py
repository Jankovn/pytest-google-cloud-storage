import pytest

import polars as pl

@pytest.fixture(scope='function')
def dummy_parquet() -> pl.DataFrame:
    return pl.DataFrame({'A': [1, 2], 'B': [3, 4]})
