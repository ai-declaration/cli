import argparse
import json
import sys

from aidecl_validate import __version__
from aidecl_validate.loader import load_file, load_schema
from aidecl_validate.schema import validate_schema
from aidecl_validate.semantic import validate_semantics
from aidecl_validate import colors

EXIT_OK = 0
EXIT_SEMANTIC_ERROR = 1
EXIT_SCHEMA_ERROR = 2
EXIT_FILE_ERROR = 3


def validate_file(filepath, schema, verbose=False):
    """Validate a single file. Returns (passed, schema_errors, warnings, sem_errors, fmt)."""
    data, fmt, err = load_file(filepath)
    if err:
        return False, [err], [], [], None

    schema_errors = validate_schema(data, schema, verbose=verbose)
    if schema_errors:
        return False, schema_errors, [], [], fmt

    warnings, sem_errors = validate_semantics(data, verbose=verbose)
    passed = len(sem_errors) == 0
    return passed, [], warnings, sem_errors, fmt


def cmd_validate(args):
    schema, err = load_schema(verbose=getattr(args, 'verbose', False))
    if err:
        print(f"Error loading schema: {err}", file=sys.stderr)
        return EXIT_FILE_ERROR

    files = args.files
    results = []
    worst_exit = EXIT_OK

    for fpath in files:
        passed, schema_errs, warns, sem_errs, fmt = validate_file(
            fpath, schema, verbose=getattr(args, 'verbose', False))

        result = {
            "file": fpath,
            "passed": passed and len(schema_errs) == 0,
            "format": fmt,
            "schema_errors": schema_errs,
            "semantic_errors": sem_errs,
            "warnings": warns,
        }
        results.append(result)

        if schema_errs:
            worst_exit = max(worst_exit, EXIT_SCHEMA_ERROR if not schema_errs[0].startswith("file") else EXIT_FILE_ERROR)
        elif sem_errs:
            worst_exit = max(worst_exit, EXIT_SEMANTIC_ERROR)

        output_fmt = getattr(args, 'output_format', 'text')
        quiet = getattr(args, 'quiet', False)

        if quiet:
            continue

        if output_fmt == "json":
            print(json.dumps(result, indent=2))
        elif output_fmt == "github-actions":
            _print_github_actions(result)
        else:
            _print_text(result, verbose=getattr(args, 'verbose', False))

    if not getattr(args, 'quiet', False) and len(files) > 1:
        ok = sum(1 for r in results if r["passed"])
        print(f"\nResults: {ok}/{len(files)} files passed")

    strict = getattr(args, 'strict', False)
    if strict and any(r["warnings"] for r in results):
        worst_exit = max(worst_exit, EXIT_SEMANTIC_ERROR)

    return worst_exit


def _print_text(result, verbose=False):
    fpath = result["file"]
    fmt = result["format"] or "?"

    if result["schema_errors"]:
        label = colors.colorize("FAIL", colors.RED)
        print(f"{label} [{fmt}]: {fpath}")
        for e in result["schema_errors"]:
            print(f"    {e}")
    elif result["semantic_errors"]:
        label = colors.colorize("FAIL", colors.RED)
        print(f"{label} [{fmt}]: {fpath}")
        for e in result["semantic_errors"]:
            print(f"    {e}")
    elif result["warnings"]:
        label = colors.colorize("PASS", colors.GREEN)
        warn = colors.colorize("(with warnings)", colors.YELLOW)
        print(f"{label} {warn} [{fmt}]: {fpath}")
        if verbose:
            for w in result["warnings"]:
                print(f"    {w}")
        else:
            print(f"    {len(result['warnings'])} warning(s)")
    else:
        label = colors.colorize("PASS", colors.GREEN)
        print(f"{label} [{fmt}]: {fpath}")


def _print_github_actions(result):
    fpath = result["file"]
    for e in result["schema_errors"] + result["semantic_errors"]:
        print(f"::error file={fpath}::{e}")
    for w in result["warnings"]:
        print(f"::warning file={fpath}::{w}")


def main():
    parser = argparse.ArgumentParser(
        prog="aidecl-validate",
        description="CLI for AI Declaration (aidecl) files",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--quiet", action="store_true", help="suppress output, only set exit code")
    parser.add_argument("--no-color", action="store_true", help="disable color output")
    parser.add_argument("--schema-url", help="custom schema URL or file path")

    sub = parser.add_subparsers(dest="command")

    # validate
    p_val = sub.add_parser("validate", help="check declaration files against schema")
    p_val.add_argument("files", nargs="+", help="files to validate")
    p_val.add_argument("-v", "--verbose", action="store_true")
    p_val.add_argument("-f", "--output-format", choices=["text", "json", "github-actions"], default="text")

    # convert
    p_conv = sub.add_parser("convert", help="convert between YAML and JSON")
    p_conv.add_argument("file", help="input file")
    p_conv.add_argument("-f", "--output-format", choices=["json", "yaml"], required=True)
    p_conv.add_argument("-o", "--output", help="output file path")

    # init
    p_init = sub.add_parser("init", help="create a new declaration file")
    p_init.add_argument("-f", "--format", choices=["yaml", "json"], default="yaml")
    p_init.add_argument("-o", "--output", help="output file path")

    args = parser.parse_args()

    if args.no_color:
        colors.disable()

    # backwards compat: no subcommand + positional args -> validate
    if args.command is None:
        # reparse with files as positional
        args.files = []
        remaining = sys.argv[1:]
        remaining = [a for a in remaining if not a.startswith("-")]
        if remaining:
            args.command = "validate"
            args.files = remaining
            args.verbose = "--verbose" in sys.argv or "-v" in sys.argv
            args.output_format = "text"
        else:
            parser.print_help()
            return 0

    from aidecl_validate.converter import cmd_convert
    from aidecl_validate.init_cmd import cmd_init

    if args.command == "validate":
        sys.exit(cmd_validate(args))
    elif args.command == "convert":
        sys.exit(cmd_convert(args))
    elif args.command == "init":
        sys.exit(cmd_init(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
