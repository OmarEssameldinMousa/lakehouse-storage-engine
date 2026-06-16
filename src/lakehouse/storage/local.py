from lakehouse.storage.base import StorageBackend
from lakehouse.errors import FileAlreadyExists
import os 
import uuid


class LocalFSBackend(StorageBackend):
    
    def __init__(self, root: str):
        self.root = root

    def get(self, path: str) -> bytes: 
        try :
            with open(os.path.join(self.root, path), 'rb') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
        
    def put(self, path: str, data: bytes) -> None:
        """Write `data` to the file at `path`. Overwrite if exists."""
        os.makedirs(os.path.dirname(os.path.abspath(os.path.join(self.root, path))), exist_ok=True)
        
        tmp_pth = os.path.join(self.root, path) + f"{uuid.uuid4().hex}.tmp"
        full_pth = os.path.join(self.root, path)
        try:
            with open(tmp_pth, 'wb') as f:
                f.write(data)
            os.replace(tmp_pth, full_pth)  # atomic operation
        except Exception as e:
            if os.path.exists(tmp_pth):
                os.remove(tmp_pth)
            raise e

    def put_if_absent(self, path: str, data: bytes) -> None:
        full_path = os.path.join(self.root, path)

        os.makedirs(os.path.dirname(os.path.abspath(full_path)), exist_ok=True)

        tmp_file = full_path + f".tmp-{uuid.uuid4()}"
        try:
            with open(tmp_file, 'wb') as f:
                f.write(data) # write data to temp file
                f.flush() # ensure data is flushed to OS buffers
                os.fsync(f.fileno()) # ensure data is written to disk
            os.link(tmp_file, full_path)
        except FileExistsError:
            raise FileAlreadyExists(f"File already exists: {path}")
        finally:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)  # clean up temp file

    def exists(self, path: str) -> bool:
        return os.path.exists(os.path.join(self.root, path))

    def list(self, prefix: str) -> list[str]:
        if not self.exists(prefix):
            return []
        
        paths = []
        absolute_root = os.path.abspath(self.root)

        for root, _, files in os.walk(os.path.join(self.root, prefix)):
            for file in files:
                full_system_path = os.path.abspath(os.path.join(root, file))
                
                relative_path = os.path.relpath(full_system_path, absolute_root)
                paths.append(relative_path)
        return paths
    
    def delete(self, path: str) -> None: 
        try:
            os.remove(os.path.join(self.root, path))
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
