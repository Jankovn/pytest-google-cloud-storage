# Introduction
Pytest custom features, e.g. fixtures and various tests. Aimed to emulate Google Cloud Storage service

## Requirements / Resources
- Docker
- [fsouza/fake-gcs-server](https://github.com/fsouza/fake-gcs-server) Emulates Google Cloud Storage
- Python >= 3.11
- Unix/MacOS environment

# Usage
The project involves the development of a custom pytest plugin that emulates the Google Cloud Storage (GCS) service to support streamlined testing workflows.

It is built on top of the original [docker image](https://github.com/fsouza/fake-gcs-server) that handles natively [google-cloud-storage](https://github.com/googleapis/python-storage) functionality,
with the project adding the necessary internal configuration to integrate seamlessly with Polars.

Originally designed to validate [Polars DataFrame](https://github.com/pola-rs/polars) read/write operations in a simulated remote environment,
the plugin enables efficient testing without relying on actual cloud infrastructure.

This setup allows for comprehensive integration testing that closely mirrors real-world cloud interactions.

## Run the emulator manually
```bash
# If you intend to run the image without passing by pytest
docker run -v /tmp/data:/data -d -p 9023:9023 --name storage_emulator fsouza/fake-gcs-server -port 9023 -scheme http -backend memory -public-host 127.0.0.1:9023 -external-url http://127.0.0.1:9023 -filesystem-root /storage
```
The parameters are exactly the same as the docker command in the ``plugin.py`` file.

# Linter

Ruff is the default Python linter used in the project.

If you want to check it, just run ``ruff check``.

All ruff configuration are stored in the ``pyproject.toml`` file.

## The ``check`` command can be added as a pre-commit hook
If by any mean you forget to check the syntax of your code before committing it,
the ``.pre-commit-config.yaml`` will call ``ruff check``.
This avoids unnecessary commits that correct the fact that you forgot to apply the command.

```bash
# Install pre-commit
python3 -m pip install pre-commit
# Install ruff pre-commit in git correct path 
python3 -m pre-commit install
```

# How to test the plugin
Under the folder ``tests`` you'll find common and small tests used to give you the possibility and the usage you can have.


# Appendix

Below, find attached 

* Additional resources that helped building this plugin:
    * Existing cloud storage emulator
      - https://github.com/oittaa/gcp-storage-emulator
    * Github conversation
      - https://github.com/apache/arrow-rs/issues/5263
    * Github code
      - https://github.com/pola-rs/polars/blob/2db0ba608b223a014bba5e10d7b82505898798ed/docs/releases/upgrade/0.20.md?plain=1#L502
      - https://docs.rs/object_store/0.12.0/object_store/gcp/struct.GoogleCloudStorageBuilder.html
      - https://github.com/fsspec/gcsfs/blob/1543ab4fcc4b17fcaa680abab0e93fed33980e21/gcsfs/core.py#L161
    * Similar services relying on other cloud provider
      - https://www.localstack.cloud/
      - https://min.io/
