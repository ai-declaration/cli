"""aidecl: CLI tool for AI Declaration files."""

__version__ = "0.3.0"

from aidecl.loader import load_file, load_schema
from aidecl.schema import validate_schema
from aidecl.semantic import validate_semantics

__all__ = ["load_file", "load_schema", "validate_schema", "validate_semantics"]
