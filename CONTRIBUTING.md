# Contributing to statanim

Thank you for your interest in contributing!

## Ways to Contribute
- Report bugs via [GitHub Issues](https://github.com/rishabhbhartiya/statanim/issues)
- Request new statistical visualisations
- Submit pull requests for new distributions, charts, or props

## Adding a New Distribution
1. Inherit from `BaseDistribution3D`
2. Implement `pdf`/`pmf`, `cdf`, `mean`, `variance`
3. Add a demo scene in `scenes/demo_distributions.py`
4. Add tests in `tests/`

## Adding a New Prop
1. Inherit from the base prop class
2. Implement built-in animations
3. Add a demo scene

## Pull Request Process
1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Open a PR with a clear description

## Code Style
- Follow PEP 8
- Use type hints
- Docstrings for all public classes and methods

## Questions?
Open a [GitHub Discussion](https://github.com/rishabhbhartiya/statanim/discussions)
or email rishabh.bhartiya.in@gmail.com