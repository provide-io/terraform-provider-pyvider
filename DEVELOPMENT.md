# Terraform Provider Pyvider - Development Guide

This guide covers the complete development workflow for building, testing, and distributing the terraform-provider-pyvider from a clean environment.

## Prerequisites

- **Python 3.11+**: Required for the provider runtime
- **uv**: Modern Python package manager ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Git**: For version control and workspace dependencies

## Quick Start

From a completely clean environment, you can build the entire provider with documentation:

```bash
# Start fresh
make clean-all

# Set up development environment
make venv          # Create virtual environment
make setup         # Add workspace dependencies
make deps          # Install all dependencies
make docs          # Generate documentation
```

## Available Make Targets

### 🔧 Environment Setup

| Target | Description |
|--------|-------------|
| `make venv` | Create `.venv` virtual environment using `uv venv` |
| `make activate` | Show command to activate the environment |
| `make setup` | Add workspace dependencies via `uv add` |
| `make deps` | Install all dependencies with `uv sync --all-groups --dev` |

### 📚 Documentation

| Target | Description |
|--------|-------------|
| `make docs` | Generate function documentation using plating |
| `make clean-docs` | Clean documentation directory |
| `make docs-serve` | Build and serve docs locally on port 8000 |

### 🏗️ Build & Package

| Target | Description |
|--------|-------------|
| `make build` | Build the provider PSP package |
| `make keys` | Generate signing keys if missing |
| `make install-flavor` | Install flavorpack tool via `uv tool` |

### 🧪 Testing

| Target | Description |
|--------|-------------|
| `make test` | Test the provider binary |
| `make test-local` | Test with local Terraform |
| `make lint` | Run code linting |
| `make format` | Format code |

### 🧹 Cleanup

| Target | Description |
|--------|-------------|
| `make clean` | Clean build artifacts |
| `make clean-all` | Deep clean including `.venv`, docs, and caches |
| `make clean-docs` | Clean documentation directory |
| `make clean-workenv` | Clean flavor work environments |

### 🚀 Workflows

| Target | Description |
|--------|-------------|
| `make all` | Complete development cycle: clean → setup → docs → build → test |
| `make dev` | Quick development setup: venv → setup → deps → build → install |

## Development Workflow

### Starting Fresh

When starting development from scratch or after a `git clean`:

```bash
# 1. Clean everything
make clean-all

# 2. Set up environment
make venv
make setup
make deps

# 3. Generate documentation
make docs

# 4. Build provider (if flavorpack is working)
make build
```

### Daily Development

For ongoing development work:

```bash
# Activate environment
source .venv/bin/activate

# Make your changes...

# Regenerate docs after code changes
make docs

# Test changes
make test-local

# Format and lint
make format lint
```

### Environment Management

The Makefile automatically manages the Python environment:

- **Virtual Environment**: Creates `.venv/` using `uv venv`
- **Workspace Dependencies**: Adds local packages via `uv add`
- **Automatic Activation**: All targets activate `.venv` before execution

#### Workspace Dependencies Added by `make setup`:

- `provide-foundation` - Core foundation utilities
- `pyvider-components` - Terraform provider components
- `plating` - Documentation generation system
- `flavorpack` - Binary packaging system

## Documentation Generation

The provider uses the **plating** system for generating Terraform documentation:

### What Gets Generated

```
docs/
├── functions/          # Individual function docs (19 files)
│   ├── add.md         # add(a, b) - Adds two numbers
│   ├── min.md         # min(numbers) - Finds minimum value
│   ├── round.md       # round(number, precision) - Rounds number
│   └── ...
└── index.md           # Provider overview (auto-generated)
```

### Documentation Features

- **Accurate Signatures**: Function signatures match actual implementation
- **Realistic Examples**: `min([1, 3, 5, 2, 4]) # Returns: 1`
- **Terraform Format**: Compatible with Terraform Registry documentation
- **Individual Files**: Each function gets its own `.md` file

### Customizing Documentation

The documentation generation uses the plating API:

```python
from plating import Plating, PlatingContext

context = PlatingContext(provider_name="pyvider")
plating = Plating(context, package_name="pyvider.components")

# Generate documentation
result = await plating.plate(output_dir="docs")
```

## Dependency Management

### Workspace Structure

The provider depends on several workspace siblings:

```
provide-io/
├── terraform-provider-pyvider/    # This provider
├── pyvider-components/            # Component library
├── plating/                       # Documentation system
├── provide-foundation/            # Core utilities
└── flavorpack/                    # Packaging system
```

### How Dependencies Are Added

The `make setup` target uses `uv add` to add workspace dependencies:

```bash
uv add provide-foundation pyvider-components plating flavorpack
```

This automatically:
- Adds dependencies to `pyproject.toml`
- Creates `[tool.uv.sources]` workspace entries
- Installs packages in editable mode

### Manual Dependency Management

If you need to add or modify dependencies:

```bash
# Activate environment first
source .venv/bin/activate

# Add new dependencies
uv add package-name

# Add development dependencies
uv add --dev pytest ruff mypy

# Install local packages in editable mode
uv pip install -e ../other-workspace-project
```

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'plating'"**
```bash
# Ensure plating is installed
source .venv/bin/activate
uv pip install -e ../plating
```

**"Virtual environment already exists"**
```bash
# Clean and recreate if needed
make clean-all
make venv
```

**"uv add" warnings about VIRTUAL_ENV mismatch**
```bash
# This is expected and can be ignored
# uv detects parent directory .venv but uses project-specific environment
```

### Known Issues

**Flavorpack Build Error**
- The `make build` target may fail due to provide-foundation version conflicts
- Documentation generation works perfectly
- Binary packaging is a separate concern from core development

**Resource Documentation**
- Currently only function documentation is generated
- Resource/data source docs need schema variable fixes

### Getting Help

**Check Environment Status**:
```bash
source .venv/bin/activate && python --version
```

**Reset Everything**:
```bash
make clean-all     # Nuclear option - removes everything
make dev           # Quick rebuild
```

## Project Structure

```
terraform-provider-pyvider/
├── .venv/                 # Virtual environment (created by make venv)
├── plating/               # Documentation source and templates
│   ├── guides/           # Source for manually-written guides
│   ├── partials/         # Reusable documentation snippets
│   └── templates/        # Provider-level templates
├── docs/                  # Generated documentation (DO NOT EDIT)
│   ├── data-sources/     # Data source documentation
│   ├── functions/        # Function documentation
│   ├── guides/           # Copied from plating/guides/
│   ├── resources/        # Resource documentation
│   └── index.md          # Provider overview
├── examples/              # Generated Terraform example configurations
│   ├── data_source/      # Data source examples
│   ├── function/         # Function examples
│   └── resource/         # Resource examples
├── keys/                  # Signing keys (generated)
├── scripts/               # Build and utility scripts
├── .github/               # GitHub Actions workflows
├── Makefile              # Development workflow automation
├── pyproject.toml        # Project configuration and dependencies
├── pyvider.toml          # Pyvider provider configuration
└── README.md             # Project overview
```

## Next Steps

1. **Development**: Start coding with `make dev`
2. **Documentation**: Regenerate docs with `make docs` after changes
3. **Testing**: Validate changes with `make test-local`
4. **Distribution**: Package with `make build` (when flavorpack is fixed)

## Contributing

When contributing to the provider:

1. Start with `make clean-all && make dev`
2. Make your changes
3. Run `make docs` to update documentation
4. Test with `make test-local`
5. Format with `make format lint`
6. Submit pull request

The Makefile ensures consistent development environments across all contributors.