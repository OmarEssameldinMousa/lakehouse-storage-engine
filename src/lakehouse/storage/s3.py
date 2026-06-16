import lakehouse.storage.base as base
from lakehouse.errors import FileAlreadyExists

class S3Backend(base.StorageBackend):
    # not impelemented error
    def get(self, path: str) -> bytes:
        raise NotImplementedError("S3Backend.get is not implemented yet")
    
    def put(self, path: str, data: bytes) -> None:
        raise NotImplementedError("S3Backend.put is not implemented yet")
    
    def put_if_absent(self, path: str, data: bytes) -> None:
        raise NotImplementedError("S3Backend.put_if_absent is not implemented yet")
    
    def exists(self, path: str) -> bool:
        raise NotImplementedError("S3Backend.exists is not implemented yet")
    
    def list(self, prefix: str) -> list[str]:
        raise NotImplementedError("S3Backend.list is not implemented yet")
    
    def delete(self, path: str) -> None:
        raise NotImplementedError("S3Backend.delete is not implemented yet")
    
    