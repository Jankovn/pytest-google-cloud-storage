import pkg_resources

import pytest

import polars as pl

from google.cloud import storage
from pydantic_settings import BaseSettings
from typing import Generator


try:
    pkg_resources.get_distribution('pytest-google-cloud-storage')
except pkg_resources.DistributionNotFound:
    pytest_plugins = ('pytest_gcs.storage.plugin',)


@pytest.fixture(scope='session', autouse=True)
def create_bucket(storage_emulator: Generator, storage_env: BaseSettings) -> Generator:
    bucket = storage.Client().create_bucket(storage_env.BUCKET_NAME)
    yield
    bucket.delete(force=True)


@pytest.fixture(scope='function')
def dummy_parquet() -> pl.DataFrame:
    return pl.DataFrame({'A': [1, 2], 'B': [3, 4]})
