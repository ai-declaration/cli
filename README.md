# aidecl-validate

Command-line tool for validating, converting, and creating AI Declaration (aidecl) files.

AI Declaration files describe how AI tools were used in the creation of software, datasets, documents, and other digital work. This CLI validates them against the [schema](https://github.com/ai-declaration/schema) with both structural (JSON Schema) and semantic checks.

## Installation

```bash
pip install aidecl-validate
```

For development:

```bash
git clone https://github.com/ai-declaration/cli.git
cd aidecl-validate
pip install -e ".[dev]"
```

## Quick Start

```bash
# Create a new declaration file
aidecl-validate init --format yaml

# Edit aidecl.yaml with your project details

# Validate it
aidecl-validate validate aidecl.yaml
```

## Usage

### validate

Check one or more declaration files against the schema:

```bash
aidecl-validate validate aidecl.yaml
aidecl-validate validate aidecl.json another.yaml
aidecl-validate validate --verbose aidecl.yaml
aidecl-validate validate --output-format json aidecl.yaml
aidecl-validate validate --strict aidecl.yaml  # warnings become errors
aidecl-validate validate --quiet aidecl.yaml    # only exit code, no output
```

Sample output:

```
PASS [yaml]: aidecl.yaml
```

```
FAIL [yaml]: aidecl.yaml
    Schema error at 'ai_usage.level': 'high' is not valid. Allowed values: 'none', 'minimal', 'moderate', 'significant', 'extensive'
```

### convert

Convert between YAML and JSON:

```bash
aidecl-validate convert aidecl.yaml -f json
aidecl-validate convert aidecl.json -f yaml -o output.yaml
```

### init

Create a template declaration file:

```bash
aidecl-validate init
aidecl-validate init --format json
aidecl-validate init --output my-project.yaml
```

The init command auto-detects your project name and git config for sensible defaults.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All files valid |
| 1 | Semantic errors found |
| 2 | Schema validation errors |
| 3 | File errors (not found, binary, too large) |

## Output Formats

**text** (default): Human-readable colored output.

**json**: Machine-readable output per file:
```json
{
  "file": "aidecl.yaml",
  "passed": true,
  "schema_errors": [],
  "semantic_errors": [],
  "warnings": ["declaration date is in the future: 2099-01-01"]
}
```

**github-actions**: Annotation format for CI:
```
::error file=aidecl.yaml::used is false but tools are listed
::warning file=aidecl.yaml::declaration date is in the future
```

## Validation Rules

### Schema checks

Validates structure against JSON Schema Draft 2020-12: required fields, types, enum values, string formats, conditional requirements (e.g. `summary` required when `used: true`).

### Semantic checks

| # | Level | Rule |
|---|-------|------|
| 1 | warn | AI usage declared but no tools listed |
| 2 | error | `used: false` but tools present |
| 3 | error | `used: false` but level is not `none` |
| 4 | warn | `code_proportion` percentages don't sum to ~100 |
| 5 | warn | Declaration date is in the future |
| 6 | warn | Review date is after declaration date |
| 7 | warn | Security review performed but no review type |
| 8 | warn | Personal data sent without DPA |
| 9 | warn | Level is `extensive` but no proportion data |
| 10 | warn | Component references tool not in tools list |
| 11 | warn | Schema version newer than supported |
| 12 | error | Tool period end before start |
| 13 | warn | Tool trains on data but no data handling section |
| 14 | warn | Next review date is in the past |

## Integration

### GitHub Actions

```yaml
- name: Validate AI Declaration Format
  run: |
    pip install aidecl-validate
    aidecl-validate validate --output-format github-actions aidecl.yaml
```

### Pre-commit framework

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/ai-declaration/cli
    rev: v0.1.0
    hooks:
      - id: aidecl-validate
```

### Git pre-commit hook

```bash
#!/bin/sh
aidecl-validate validate aidecl.yaml --quiet
```

## Related Standards

| Standard | Relationship |
|----------|-------------|
| codemeta.json | Project metadata; aidecl adds AI transparency |
| CITATION.cff | Citation metadata; complementary |
| SPDX 3.0 AI Profile | License + AI BOM; aidecl is lighter for declarations |
| CycloneDX ML-BOM | ML component inventory; different scope |
| C2PA | Content authenticity; media-focused |
| W3C PROV | Provenance ontology; aidecl JSON-LD maps to PROV-O |

## Related Projects

- [schema](https://github.com/ai-declaration/schema) -- Schema definition and examples
- [web](https://github.com/ai-declaration/web) -- Web-based generator and validator

## Shell Completions

Bash:
```bash
eval "$(register-python-argcomplete aidecl-validate)"
```

Or add to your `.bashrc` for persistent completions.

Fish and Zsh: use `argcomplete` or generate completions manually from the `--help` output.

## Privacy Note

The `declared_by` field identifies who made the declaration. For public repositories, consider using team names or roles instead of individual names.

## Compatibility

| aidecl-validate version | Supported schema versions |
|------------------------|--------------------------|
| 0.1.x | 1.0.0 |

## Development

```bash
pip install -e ".[dev]"
pytest
pytest --cov
```

## License

Apache-2.0. The bundled `schema.json` is from [schema](https://github.com/ai-declaration/schema) (CC BY-SA 4.0).
