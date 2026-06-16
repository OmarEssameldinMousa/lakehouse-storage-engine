# a log writer + reader for the lakehouse protocol
import json
from typing import Any, Dict, List, Optional
from lakehouse.storage.base import StorageBackend
from lakehouse.protocol.paths import commit_path
from lakehouse.protocol.actions import to_json, from_json



def write_commit(backend: StorageBackend, version: int, actions: List[Dict[str, Any]]) -> None:
    """Write a commit log entry for the given version and actions."""
    lines = [to_json(action) for action in actions]

    log_content = "\n".join(lines) + "\n"

    log_data = log_content.encode('utf-8')
    backend.put_if_absent(commit_path(version), log_data)

def read_commit(backend: StorageBackend, version: int) -> Optional[Dict[str, Any]]:
    """Read the commit log entry for the given version. Returns None if not found."""
    try:
        log_data = backend.get(commit_path(version))
        log_content = log_data.decode('utf-8')
        lines = log_content.strip().splitlines()
        actions = [from_json(line) for line in lines]
        return actions
    except FileNotFoundError:
        return None
        
        