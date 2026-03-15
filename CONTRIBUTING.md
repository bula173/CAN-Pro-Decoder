# Contributing to CAN Pro-Decoder

Thank you for your interest in contributing to CAN Pro-Decoder! This guide will help you set up your development environment and contribute effectively.

## Development Setup

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd CAN-Pro-Decoder
   ```

2. **Run the automated setup script**:
   ```bash
   python setup_dev.py
   ```

   This script will:
   - Create a virtual environment
   - Install all dependencies (production + development)
   - Install pre-commit hooks
   - Validate your setup

3. **Activate the virtual environment**:

   **Windows**:
   ```bash
   .\venv\Scripts\activate
   ```

   **macOS/Linux**:
   ```bash
   source venv/bin/activate
   ```

### Manual Setup (if needed)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# (Windows: .\venv\Scripts\activate)
# (Unix: source venv/bin/activate)

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Code Style & Quality

This project uses modern Python development tools to maintain code quality:

### Tools Used

- **Black**: Code formatter (opinionated, zero-config)
- **Ruff**: Fast Python linter
- **Mypy**: Static type checker
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks for quality enforcement

### Before Committing

The pre-commit hooks will automatically check your code. You can also run checks manually:

```bash
# Format code
black .

# Check for linting issues
ruff check . --fix

# Type check
mypy .

# Run tests
pytest -v
```

### Code Style

- **Line Length**: 100 characters (enforced by Black)
- **Indentation**: 4 spaces
- **Imports**: Alphabetically sorted (handled by Ruff)
- **Type Hints**: Encouraged but not mandatory for GUI code

### Pre-commit Hooks

When you commit, these hooks automatically run:

1. **Whitespace**: Removes trailing whitespace
2. **YAML/JSON**: Validates syntax
3. **Black**: Formats code
4. **Ruff**: Lints and auto-fixes issues
5. **Mypy**: Type checks code

If a hook fails, the commit is blocked. Fix the issues and try again:

```bash
git add <fixed-files>
git commit -m "your message"
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=.

# Run specific test file
pytest tests/test_parser_engine.py -v

# Run specific test
pytest tests/test_parser_engine.py::TestCANParser::test_process_asc_basic -v
```

### Test Structure

Tests are organized by module:

```
tests/
├── conftest.py              # Shared fixtures
├── test_parser_engine.py    # Parser tests
├── test_ui_components.py    # UI component tests
└── test_integration.py      # End-to-end tests
```

### Writing Tests

- Use `@pytest.mark.unit` for unit tests
- Use `@pytest.mark.gui` for GUI tests
- Use `@pytest.mark.integration` for integration tests
- The `conftest.py` provides common fixtures like `sample_dbc_db`, `temp_test_dir`

Example:

```python
@pytest.mark.unit
def test_parser_basic(self, sample_dbc_db, tmp_path):
    """Test basic parsing functionality."""
    # Your test code here
    pass
```

## Git Workflow

1. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** and commit:
   ```bash
   git add <files>
   git commit -m "Description of changes"
   ```
   Pre-commit hooks will run automatically.

3. **Push and create a Pull Request**:
   ```bash
   git push origin feature/my-feature
   ```

4. **Code review**: Address any feedback and update your PR.

## Project Structure

```
CAN-Pro-Decoder/
├── main.py                  # GUI application
├── parser_engine.py         # CAN log parsing
├── ui_components.py         # UI dialogs
├── build_exe.py             # PyInstaller configuration
├── setup_dev.py             # Development environment setup
├── pyproject.toml           # Project metadata & tool config
├── .pre-commit-config.yaml  # Pre-commit hooks config
├── .editorconfig            # Editor settings
└── tests/                   # Test suite
```

## Debugging

### VSCode Debug Configurations

Pre-configured debug configurations are available in `.vscode/launch.json`:

- **Python: Main Application**: Run the GUI app
- **Python: Pytest (All Tests)**: Run full test suite
- **Python: Pytest (Current File)**: Run tests in current file

### Adding Debug Points

Simply set breakpoints in VSCode (red dots in margin) and use the Debug configuration to run.

## Common Tasks

### Adding a New Dependency

```bash
# Add to pyproject.toml [project.dependencies]
# Then reinstall
pip install -e ".[dev]"
```

### Running the Application

```bash
python main.py
```

### Building a Windows Executable

```bash
python build_exe.py
# Output will be in dist/
```

### Type Checking Specific File

```bash
mypy parser_engine.py
```

## Troubleshooting

### "Pre-commit hook failed"

- Run `pre-commit run --all-files` to see what failed
- Fix the issues:
  - `black .` to format
  - `ruff check . --fix` to auto-fix linting
- Commit again

### "Module not found" when running tests

Make sure you've activated your venv and installed dev dependencies:

```bash
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### "pytest command not found"

Install test dependencies:

```bash
pip install pytest pytest-cov
```

## Getting Help

- Check existing issues on GitHub
- Review code comments and docstrings
- Run tests in verbose mode: `pytest -vv`
- Look at recent commits for patterns

## Code of Conduct

- Be respectful and constructive
- Follow the code style guidelines
- Write clear commit messages
- Include tests for new features
- Update documentation as needed

Thank you for contributing!
