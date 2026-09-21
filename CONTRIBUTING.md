# Contributing to aidecl

Thanks for your interest in contributing to the AI Declaration Format CLI validator.

## Reporting Issues

Open an issue on the [GitHub issue tracker](https://github.com/ai-declaration/cli/issues) with:

- Steps to reproduce the problem
- Expected vs actual behavior
- Your Python version and OS

## Proposing Changes

1. Check existing issues and pull requests first
2. For non-trivial changes, open an issue to discuss the approach
3. Once agreed, submit a pull request

## Development Setup

```bash
git clone https://github.com/ai-declaration/cli.git
cd cli
pip install -e ".[dev]"
pytest
```

## Code Style

- Python 3.12+
- 4-space indentation
- Type hints where they help readability
- Keep functions focused and names descriptive
- Follow existing patterns in the codebase

## Running Tests

```bash
pytest
pytest -v           # verbose output
pytest tests/test_semantic.py  # specific test file
```

## Pull Request Process

1. Fork the repository and create a branch from `main`
2. Make your changes and add tests for new functionality
3. Run the full test suite and make sure everything passes
4. Submit a pull request with a clear description

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Please read it before participating.

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).

## Questions

Open an issue if you have questions about contributing.
