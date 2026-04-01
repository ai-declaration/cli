import json
import subprocess
from datetime import date
from pathlib import Path

import yaml


def _git_config(key):
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def init_disclosure(output_format="yaml", output_path=None):
    """Create a new AI Declaration template file."""
    project_name = Path.cwd().name
    repo_url = _git_config("remote.origin.url") or "https://github.com/YOUR-ORG/YOUR-REPO"
    declared_by = _git_config("user.name") or "ROLE OR TEAM NAME"

    template = {
        "schema_version": "1.0.0",
        "project": {
            "name": project_name,
            "repository": repo_url,
            "content_type": "software",
        },
        "ai_usage": {
            "used": True,
            "summary": "DESCRIBE HOW AI WAS USED",
            "level": "minimal",
            "tools": [
                {
                    "name": "TOOL NAME",
                    "vendor": "VENDOR",
                    "type": "assistant",
                    "purpose": ["code completion"],
                }
            ],
            "scope": {
                "code_completion": True,
            },
        },
        "declaration": {
            "date": date.today().isoformat(),
            "declared_by": declared_by,
        }
    }

    if output_format == "json":
        ext = ".json"
        content = json.dumps(template, indent=2, ensure_ascii=False) + "\n"
    else:
        ext = ".yaml"
        header = "# AI Declaration Format (aidecl)\n"
        header += "# Use a role or team name rather than personal name if this file will be public\n\n"
        content = header + yaml.dump(template, default_flow_style=False,
                                     sort_keys=False, allow_unicode=True)

    if output_path is None:
        output_path = Path.cwd() / f"aidecl{ext}"
    else:
        output_path = Path(output_path)

    if output_path.exists():
        print(f"File already exists: {output_path}")
        return str(output_path), "file already exists"

    output_path.write_text(content, encoding="utf-8")
    print(f"Created {output_path}")
    print(f"Next: edit the file, then run 'aidecl-validate validate {output_path.name}'")
    return str(output_path), None


def cmd_init(args):
    fmt = getattr(args, 'format', 'yaml') or 'yaml'
    out = getattr(args, 'output', None)
    _, err = init_disclosure(output_format=fmt, output_path=out)
    return 1 if err else 0
