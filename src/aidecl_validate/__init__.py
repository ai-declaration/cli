"""aidecl-validate: CLI tool for AI Declaration files."""

__version__ = "0.2.0"

from aidecl_validate.loader import load_file, load_schema
from aidecl_validate.schema import validate_schema
from aidecl_validate.semantic import validate_semantics

__all__ = ["load_file", "load_schema", "validate_schema", "validate_semantics"]
