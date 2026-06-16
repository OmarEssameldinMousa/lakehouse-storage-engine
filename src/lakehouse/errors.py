class LakehouseError(Exception):
    """Base class for all lakehouse errors."""
    pass

class FileAlreadyExists(LakehouseError):
    """Raised when attempting to write a file that already exists."""
    pass

class ConcurrentWrite(LakehouseError):
    """Raised when a concurrent write is detected."""
    pass

class SchemaMismatch(LakehouseError):
    """Raised when the schema of the data being written does not match the expected schema."""
    pass

class VersionNotFound(LakehouseError):
    """Raised when a requested version of the data is not found."""
    pass

class ActionNotSupported(LakehouseError):
    """Raised when an unsupported action is attempted."""
    pass