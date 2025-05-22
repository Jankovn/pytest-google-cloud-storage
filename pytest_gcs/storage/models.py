import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any


class IntegrationDeploymentEnv(BaseSettings):
    """ Gathers all CI/CD additional variables set internally.
    """
    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="INTEGRATION_DEPLOYMENT_")
    # Run in an CI/CD environment
    ENV: str = '0'


class StorageEnv(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="STORAGE_")
    PROTOCOL: str = 'gs'
    # Override with your bucket's name
    BUCKET_NAME : str = "dummy"
    # (docker) Absolute path of host joined with relative path to storage represented by the folder 'BUCKET_NAME'
    MOUNT_ABSOLUTE_PATH: str = f'{os.path.dirname(__file__)}/data/storage'
    # Common vars used throughout object's lifetime
    CREDENTIAL_FILENAME: str = 'data/credential.json'
    CREDENTIAL_FILENAME_RELATIVE_PATH: str = 'data/credential.json'
    CREDENTIAL_FILENAME_ABSOLUTE_PATH: str = f'{os.path.dirname(__file__)}/data/credential.json'
    # Template used by Google, with the minimum requirements stored in the json
    CREDENTIAL_BODY: dict[str, Any] = {
        "gcs_base_url": "http://localhost:9023",
        "disable_oauth": True,
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "refresh_token": "",
        "client_secret": "",
        "client_id": ""
    }

