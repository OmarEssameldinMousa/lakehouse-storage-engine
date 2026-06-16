from dataclasses import asdict, dataclass
from lakehouse.errors import ActionNotSupported
import json
# Command-style action records. Each serializes to a single JSON object
# under one top-level key, e.g. {"add": {...}}. Keep them dumb data holders.

@dataclass(frozen=True)
class Protocol:
    """Reader/writer version gate. Start minViewer=1, minWriter=2."""
    min_reader_version: int
    min_writer_version: int

@dataclass(frozen=True)
class Format:
    provider: str = "parquet"
    # options: dict[str, str] — add if you need it

@dataclass(frozen=True)
class Metadata:
    """Table identity + schema. schema_string holds the serialized schema."""
    id: str
    schema_string: str
    format: Format
    partition_columns: list[str]
    # created_time, name, description: optional

@dataclass(frozen=True)
class AddFile:
    """A data file that is LIVE as of this commit."""
    path: str                # relative to table root
    size: int
    modification_time: int
    data_change: bool
    stats: str | None        # JSON string: numRecords/minValues/maxValues/nullCount
    partition_values: dict[str, str]

@dataclass(frozen=True)
class RemoveFile:
    """Tombstone. A file that WAS live and is now logically deleted.
    Keep enough info (path, deletion_timestamp) for VACUUM later."""
    path: str
    deletion_timestamp: int
    data_change: bool

@dataclass(frozen=True)
class CommitInfo:
    """Human/audit breadcrumb for history(). Not load-bearing for state."""
    timestamp: int
    operation: str
    operation_parameters: dict
    # Think: what's the minimum to reconstruct a useful history() row?

Actions = Protocol | Format | Metadata | AddFile | RemoveFile | CommitInfo

def to_json(action: Actions) -> str:
    """Convert dataclass instances to JSON-serializable dicts."""
    class_map = {
        Protocol: "protocol",
        Format: "format",
        Metadata: "metadata",
        AddFile: "add",
        RemoveFile: "remove",
        CommitInfo: "commit_info"
    }
    
    action_type = type(action)

    if action_type not in class_map:
        raise ActionNotSupported(f"Unsupported action type: {action_type}") 

    action_dict = asdict(action)

    wrapped_dict = {class_map[action_type]: action_dict}

    return json.dumps(wrapped_dict)


def from_json(json_str: str) -> Actions:
    """Deserialize JSON string to the appropriate dataclass instance."""
    data = json.loads(json_str)

    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError("Invalid JSON format for action. Expected a single top-level key.")

    action_type, action_data = list(data.items())[0]

    if action_type == "protocol":
        return Protocol(**action_data)
    elif action_type == "format":
        return Format(**action_data)
    elif action_type == "metadata":
        if "format" in action_data and isinstance(action_data["format"], dict):
            action_data["format"] = Format(**action_data["format"])
        return Metadata(**action_data)
    elif action_type == "add":
        return AddFile(**action_data)
    elif action_type == "remove":
        return RemoveFile(**action_data)
    elif action_type == "commit_info":
        return CommitInfo(**action_data)
    else:
        raise ActionNotSupported(f"Unsupported action type: {action_type}")