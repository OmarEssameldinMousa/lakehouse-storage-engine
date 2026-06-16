from abc import ABC, abstractmethod

class StorageBackend(ABC):
    """Strategy seam. Every byte of I/O in the system goes through here.

    Implementations: LocalFSBackend, S3Backend. Higher layers MUST NOT
    import os, open(), boto3, or fsspec directly.
    """

    @abstractmethod
    def get(self, path: str) -> bytes: ...

    @abstractmethod
    def put(self, path: str, data: bytes) -> None:
        """Unconditional overwrite-or-create. NOT for committing log files."""
        ...

    @abstractmethod
    def put_if_absent(self, path: str, data: bytes) -> None:
        """Atomic create. Raise FileAlreadyExists if path exists.
        This is the ONLY primitive the commit protocol is allowed to use.
        Document, in the body, the exact mechanism that makes it atomic.
        """
        ...

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Diagnostics / VACUUM only. Calling this before a write is a TOCTOU bug."""
        ...

    @abstractmethod
    def list(self, prefix: str) -> list[str]:
        """Enumerate keys under prefix. For log discovery and VACUUM. NEVER
        to enumerate active data files for a read."""
        ...

    @abstractmethod
    def delete(self, path: str) -> None: ...
