# MCP Manager - Configuration Utilities

import json
from pathlib import Path
from typing import Dict, Any, Optional

def read_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Safely reads a JSON file.

    Args:
        file_path: The path to the JSON file.

    Returns:
        A dictionary representing the JSON content, or None if the file
        doesn't exist or is not valid JSON.
    """
    if not file_path.exists():
        return None
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read or parse JSON file ","{","file_path","}",": ","{","e","}")
        return None # Treat invalid JSON as non-existent for reading purposes

def write_json_file(file_path: Path, data: Dict[str, Any]) -> None:
    """Writes data to a JSON file, creating parent directories if needed.

    Args:
        file_path: The path to the JSON file.
        data: The dictionary to write as JSON.

    Raises:
        IOError: If writing the file fails.
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4) # Use indent for readability
    except IOError as e:
        print(f"Error: Could not write JSON file ","{","file_path","}",": ","{","e","}")
        raise


