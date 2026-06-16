import pytest

@pytest.fixture
def backend(tmp_path):
    """Yield a LocalFSBackend rooted at an isolated temp dir.
    Parametrize over [LocalFS, S3/MinIO] later in M3; one backend now."""
    from lakehouse.storage.local import LocalFSBackend
    backend = LocalFSBackend(str(tmp_path))
    yield backend