import json
import hashlib
import sys
from pathlib import Path

import yaml


MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

SCHEMA_PATH = Path(__file__).parent / "data" / "schema.json"
CHECKSUM_PATH = Path(__file__).parent / "data" / "schema.json.sha256"


def load_schema(verbose=False):
    """Load the bundled JSON Schema."""
    try:
        raw = SCHEMA_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, "bundled schema.json not found"

    if verbose and CHECKSUM_PATH.exists():
        expected = CHECKSUM_PATH.read_text().strip()
        actual = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        if expected != actual:
            print(f"WARNING: schema checksum mismatch (expected {expected[:12]}..., got {actual[:12]}...)",
                  file=sys.stderr)

    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        return None, f"failed to parse bundled schema: {e}"


def load_file(filepath):
    """Load a declaration file. Returns (data, format_str, error_str)."""
    path = Path(filepath)

    if not path.exists():
        return None, None, f"file not found: {filepath}"

    try:
        size = path.stat().st_size
    except OSError as e:
        return None, None, f"cannot stat file: {e}"

    if size > MAX_FILE_SIZE:
        return None, None, f"file too large ({size} bytes, max {MAX_FILE_SIZE})"

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, None, "file appears to be binary or not UTF-8 encoded"
    except OSError as e:
        return None, None, f"cannot read file: {e}"

    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        return _parse_yaml(content)
    elif suffix == ".json":
        return _parse_json(content)
    else:
        # unknown extension, try json first then yaml
        data, fmt, err = _parse_json(content)
        if err is None:
            return data, fmt, None
        return _parse_yaml(content)


def _parse_yaml(content):
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        return None, None, f"YAML parse error: {e}"

    if not isinstance(data, dict):
        return None, None, "YAML file did not produce a mapping (got {})".format(
            type(data).__name__ if data is not None else "empty"
        )
    return data, "yaml", None


def _parse_json(content):
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return None, None, f"JSON parse error: {e}"

    if not isinstance(data, dict):
        return None, None, "JSON file did not produce an object"
    return data, "json", None
