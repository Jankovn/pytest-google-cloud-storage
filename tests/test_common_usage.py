import io
import pytest

import polars as pl

from google.cloud import storage
from polars.testing import assert_frame_equal
from typing import Generator


def test_simple_polars_io(
        storage_emulator: Generator,
        mock_read_parquet: Generator,
        mock_write_parquet: Generator,
        dummy_parquet: pl.DataFrame) -> None:
    dummy_parquet.write_parquet("gs://dummy/parquet.pq")
    assert_frame_equal(pl.read_parquet("gs://dummy/parquet.pq"), pl.DataFrame({'A': [1, 2], 'B': [3, 4]}))


@pytest.mark.parametrize('buckets', (('foo', ), ('foo', 'bar',), ('fooz', 'barz')))
def test_gcs_bucket_lifetime(storage_emulator: Generator, buckets: tuple[str]) -> None:
    _buckets = [storage.Client().create_bucket(_b) for _b in buckets]
    assert all(_b.exists() for _b in _buckets)
    _ = [_b.delete(force=True) for _b in _buckets]
    assert not all(_b.exists() for _b in _buckets)


def test_gcs_blob_lifetime(storage_emulator: Generator, dummy_parquet: pl.DataFrame) -> None:
    bucket = storage.Client().lookup_bucket(bucket_name='dummy')
    iob = io.BytesIO()
    dummy_parquet.write_parquet(iob)
    iob.seek(0)
    blob = bucket.blob('dummy.pq')
    blob.upload_from_string(iob.read())
    assert blob.exists()
    assert_frame_equal(pl.read_parquet(blob.download_as_bytes()), dummy_parquet)
    blob.delete()
    assert not blob.exists()
