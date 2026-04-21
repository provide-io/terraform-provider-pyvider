# Contributing to terraform-provider-pyvider

Thank you for your interest in contributing to terraform-provider-pyvider! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- `uv` package manager
- Terraform or OpenTofu 1.6+

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/provide-io/terraform-provider-pyvider.git
   cd terraform-provider-pyvider
   ```

2. Set up the development environment:
   ```bash
   uv sync
   ```

This will create a virtual environment and install all development dependencies.

## Development Workflow

### Running Tests

Since this provider uses components from `pyvider-components`, tests are primarily in that repository. However, you can run integration tests:

```bash
# Run all tests
we run test

# Run specific test file
uv run pytest tests/test_specific.py

# Run with coverage
we run test.coverage
```

### Building the Provider

```bash
# Build the provider binary
flavor pack

# Or using wrknv
we build

# Install to local Terraform plugin directory
we pkg install
```

The provider will be installed to:
```
~/.terraform.d/plugins/local/providers/pyvider/<version>/{platform}/
```

### Testing with Terraform

After building and installing:

```bash
cd examples/<example_name>
terraform init
terraform plan
terraform apply
```

### Code Quality

Before submitting a pull request, ensure your code passes all quality checks:

```bash
# Format code
we run format

# Lint code
we run lint

# Auto-fix linting issues
we run lint.fix

# Type check
we typecheck
```

Or manually:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/
```

### Code Style

- Follow PEP 8 guidelines (enforced by `ruff`)
- Use modern Python 3.11+ type hints (e.g., `list[str]` not `List[str]`)
- Use absolute imports, never relative imports
- Add comprehensive type hints to all functions and methods
- Write docstrings for public APIs

## Documentation

### Generating Documentation

Documentation is generated using Plating:

```bash
# Generate documentation
plating plate --output-dir docs

# Or using wrknv
we run docs.build
```

### Updating Documentation

When adding new features or changing APIs:

1. Update relevant docstrings in component code
2. Update `README.md` if adding user-facing features
3. Add examples in `examples/` directory
4. Run Plating to regenerate documentation

### Docstring Format

Use comprehensive docstrings for Terraform documentation generation:

```python
"""
Short description of what this data source does.

## Example Usage

```terraform
data "pyvider_env_variables" "shell" {
  keys = ["SHELL"]
}

output "shell_path" {
  value = data.pyvider_env_variables.shell.values["SHELL"]
}
```

## Argument Reference

- `keys` - (Required) List of environment variable names to read

## Attribute Reference

- `values` - Map of environment variable names to their values
"""
```

## Adding New Components

This provider uses components from `pyvider-components`. To add new components:

1. Add the component to the `pyvider-components` repository
2. Update the component imports in this repository
3. Add examples in the `examples/` directory
4. Generate updated documentation with Plating

## Project Structure

```
terraform-provider-pyvider/
├── src/                         # Source code (minimal wrapper)
├── examples/                    # Terraform examples
│   ├── data-sources/           # Data source examples
│   ├── resources/              # Resource examples
│   └── functions/              # Function examples
├── docs/                        # Generated documentation
│   ├── guides/                 # User guides
│   ├── data-sources/           # Data source docs
│   ├── resources/              # Resource docs
│   └── functions/              # Function docs
├── tests/                       # Integration tests
├── pyproject.toml              # Python configuration
└── soup.toml                   # Provider configuration (if exists)
```

## Submitting Changes

### Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name main
   ```

2. Make your changes and commit with clear messages:
   ```bash
   git commit -m "Add feature: description of what was added"
   ```

3. Ensure all tests pass and code quality checks pass:
   ```bash
   we run test
   we run lint
   we typecheck
   ```

4. Build and test the provider with Terraform:
   ```bash
   we build
   we pkg install
   cd examples/<relevant_example>
   terraform plan
   ```

5. Push your branch and create a pull request

6. Ensure your PR:
   - Has a clear title and description
   - References any related issues
   - Includes examples for new functionality
   - Updates documentation as needed
   - Passes all CI checks

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

Examples:
- `Add new data source for file metadata`
- `Fix provider configuration validation`
- `Update documentation for lens_jq data source`

## Code Review Process

All submissions require review. The maintainers will:

- Review code for quality, style, and correctness
- Ensure examples work correctly with Terraform
- Verify documentation is updated and accurate
- Check for breaking changes
- Test the provider with real Terraform configurations

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues and documentation first
- See [pyvider-components](https://github.com/provide-io/pyvider-components) for component development
- Refer to the project documentation in the `docs/` directory

## Related Repositories

- **[pyvider-components](https://github.com/provide-io/pyvider-components)** - Component implementations
- **[pyvider](https://github.com/provide-io/pyvider)** - Provider framework
- **[flavorpack](https://github.com/provide-io/flavorpack)** - Binary packaging
- **[plating](https://github.com/provide-io/plating)** - Documentation generation

## License

By contributing to terraform-provider-pyvider, you agree that your contributions will be licensed under the Apache-2.0 License.
