# Contributing to aidecl

Thanks for your interest in contributing.

## Reporting Bugs

Open an issue on the [GitHub issue tracker](https://github.com/ai-declaration/cli/issues) with:

- Steps to reproduce the problem
- Expected vs actual behavior
- Your Python version and OS

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b my-feature`)
3. Make changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

## Development Setup

```bash
git clone https://github.com/ai-declaration/cli.git
cd aidecl
pip install -e ".[dev]"
pytest
```

## Code Style

Follow the existing code style. Keep functions focused and names descriptive.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
