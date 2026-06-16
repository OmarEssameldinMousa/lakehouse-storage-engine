def commit_path(version: int) -> str:
    """_delta_log/<20-digit zero-padded version>.json"""
    return f"_delta_log/{version:020d}.json"