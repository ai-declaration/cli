import json
from pathlib import Path

import yaml

from aidecl_validate.loader import load_file


def convert_file(filepath, output_format, output_path=None):
    """Convert between YAML and JSON formats.

    Returns (output_path, error_str).
    """
    data, src_fmt, err = load_file(filepath)
    if err:
        return None, err

    p = Path(filepath)
    if output_path is None:
        ext = ".json" if output_format == "json" else ".yaml"
        output_path = p.with_suffix(ext)
    else:
        output_path = Path(output_path)

    if output_format == "json":
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    else:
        # drop @context for yaml (JSON-LD specific)
        if "@context" in data:
            data = {k: v for k, v in data.items() if k != "@context"}
        content = yaml.dump(data, default_flow_style=False,
                            sort_keys=False, allow_unicode=True)

    output_path.write_text(content, encoding="utf-8")
    print("Converted {} -> {}".format(filepath, output_path))
    return str(output_path), None


def cmd_convert(args):
    _, err = convert_file(args.file, args.output_format,
                          getattr(args, 'output', None))
    if err:
        print(f"Error: {err}")
        return 1
    return 0
