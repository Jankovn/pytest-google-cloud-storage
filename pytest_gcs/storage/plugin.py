import os
import logging

import pytest
import docker
import typing

import polars as pl

from gcsfs import GCSFileSystem
from polars import DataFrame
from docker.errors import NotFound


from pytest_gcs.storage import logging_strings as logstr
from pytest_gcs.storage import models
from pytest_gcs.storage import ctyping


PYTEST_STORAGE_LOGGER = logging.getLogger('PYTEST_STORAGE_LOGGER')


@pytest.fixture(scope='session')
def monkeypatch_session() -> ctyping.GMonkeyPatch:
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope='function')
def monkeypatch_function(monkeypatch: pytest.MonkeyPatch) -> ctyping.GMonkeyPatch:
    m = pytest.MonkeyPatch()
    yield m
    m.undo()


@pytest.fixture(scope='session')
def cicd_env() -> models.IntegrationDeploymentEnv:
    return models.IntegrationDeploymentEnv()


@pytest.fixture(scope='session', autouse=True)
def del_google_credential_env(monkeypatch_session: pytest.MonkeyPatch) -> None:
    """
    Deactivate 'GOOGLE_APPLICATION_CREDENTIALS' env var if unintentionally set.
    """
    try:
        monkeypatch_session.delenv('GOOGLE_APPLICATION_CREDENTIALS')
    except KeyError:
        PYTEST_STORAGE_LOGGER.warning(logstr.GCP_CREDENTIALS_ENV_VAR_NOT_SET)


@pytest.fixture(scope='session')
def storage_env() -> models.StorageEnv:
    """ Gather every global variables, used or referred, to google Storage. These variables will act as env vars.
    """
    return models.StorageEnv()


@pytest.fixture(scope='session')
def storage_emulator(
        storage_env: models.StorageEnv,
        cicd_env: models.IntegrationDeploymentEnv,
        monkeypatch_session: pytest.MonkeyPatch) -> typing.Generator:
    """ Set a local filesystem in order to emulate Google Cloud Storage service. With docker helps.

    Previously we used this package 'gcp-storage-emulator' to emulate the storage service.
    Not anymore, due to polars >= 0.20.0 breaking changes regarding remote files.
    Therefore, we're using a docker image that handles both legacy and polars' breaking change behavior.
    """
    # Gateway set for any remote files manipulation through fsspec or google-cloud-storage packages
    monkeypatch_session.setenv('STORAGE_EMULATOR_HOST', 'http://localhost:9023')
    # with polars versions >= 0.20.0 fsspec is not used as a gateway to administrate remote files
    # https://github.com/pola-rs/polars/blob/2db0ba608b223a014bba5e10d7b82505898798ed/docs/releases/upgrade/0.20.md?plain=1#L502
    # https://docs.rs/object_store/0.12.0/object_store/gcp/struct.GoogleCloudStorageBuilder.html
    monkeypatch_session.setenv(
        'GOOGLE_SERVICE_ACCOUNT_KEY',
        f"{os.path.dirname(__file__)}/{storage_env.CREDENTIAL_FILENAME_RELATIVE_PATH}")
    container = None
    if cicd_env.ENV == '0':
        docker_client = docker.from_env()
        try:
            _id = docker_client.containers.get('storage_emulator')
            if _id.attrs['State']['Running'] and _id.attrs['State']['Paused']:
                _id.unpause()
            elif not _id.attrs['State']['Running']:
                _id.remove()
                raise NotFound
        except NotFound:
            container = docker_client.containers.run(
                "fsouza/fake-gcs-server",
                command="-port 9023 -scheme http -backend memory -log-level debug -public-host 127.0.0.1:9023 "
                        "-external-url http://127.0.0.1:9023 -filesystem-root /storage",
                remove=True,
                detach=True,
                name="storage_emulator",
                ports={'9023/tcp': 9023},
                volumes=[f'{storage_env.MOUNT_ABSOLUTE_PATH}:/data'])
    yield
    monkeypatch_session.delenv('STORAGE_EMULATOR_HOST')
    monkeypatch_session.delenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    if container is not None:
        container.stop()


@pytest.fixture(scope='session')
def mock_polars_io(monkeypatch_session: pytest.MonkeyPatch) -> GCSFileSystem:
    return GCSFileSystem(token='anon', endpoint_url=os.environ['STORAGE_EMULATOR_HOST'])


@pytest.fixture(scope='function')
def pl_read_parquet() -> pl.io.parquet.functions:
    return pl.read_parquet


@pytest.fixture(scope='function')
def mock_read_parquet(
        monkeypatch_function: pytest.MonkeyPatch,
        pl_read_parquet: pl.io.parquet.functions,
        mock_polars_io: GCSFileSystem,
        storage_env: models.StorageEnv) -> typing.Generator:

    def _read_parquet(path: str, **k: dict) -> pl.DataFrame:
        with mock_polars_io.open(path.removeprefix(f'{storage_env.PROTOCOL}://'), 'rb') as f:
            return pl_read_parquet(f, **k)

    monkeypatch_function.setattr(pl, 'read_parquet', _read_parquet)
    yield


@pytest.fixture(scope='function')
def df_write_parquet() -> pl.functions:
    return pl.DataFrame.write_parquet


@pytest.fixture(scope='function')
def mock_write_parquet(
        monkeypatch_function: pytest.MonkeyPatch,
        df_write_parquet: pl.functions,
        mock_polars_io: GCSFileSystem,
        storage_env: models.StorageEnv) -> typing.Generator:

    def _write_parquet(df: pl.DataFrame, path: str, **k: dict) -> None:
        with mock_polars_io.open(path.removeprefix(f'{storage_env.PROTOCOL}://'), 'wb') as f:
            return df_write_parquet(df, f, **k)

    monkeypatch_function.setattr(DataFrame, 'write_parquet', _write_parquet)
    yield
