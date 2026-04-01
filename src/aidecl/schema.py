from jsonschema import Draft202012Validator
from referencing import Registry


def validate_schema(data, schema, verbose=False):
    """Validate data against the aidecl JSON Schema.

    Returns list of error strings. Empty list means valid.
    Remote $ref resolution is disabled for security.
    """
    registry = Registry()
    validator = Draft202012Validator(schema, registry=registry)

    try:
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    except Exception as e:
        return [f"validation error: {e}"]

    result = []
    for err in errors:
        path = ".".join(str(p) for p in err.absolute_path) or "(root)"
        msg = _format_error(err)
        result.append(f"Schema error at '{path}': {msg}")

        if verbose and err.context:
            for sub in err.context:
                sub_path = ".".join(str(p) for p in sub.absolute_path) or path
                result.append(f"  - at '{sub_path}': {sub.message}")

    return result


def _format_error(err):
    msg = err.message

    # make enum errors more readable
    if err.validator == "enum" and err.validator_value:
        val = err.instance
        allowed = err.validator_value
        msg = f"'{val}' is not valid. Allowed values: {', '.join(repr(v) for v in allowed)}"

        # suggest closest match for strings
        if isinstance(val, str):
            for a in allowed:
                if isinstance(a, str) and a.startswith(val[:3]):
                    msg += f" (did you mean '{a}'?)"
                    break

    elif err.validator == "type":
        expected = err.validator_value
        actual = type(err.instance).__name__
        msg = f"expected {expected}, got {actual}"

    return msg
