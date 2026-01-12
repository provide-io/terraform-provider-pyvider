# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The official Pyvider provider, built with Pyvider. This is a reference implementation and meta-provider that showcases the Pyvider framework capabilities.

**Provider name:** `pyvider`

**Components:** Uses components from `pyvider-components` package.

## Development Setup

```bash
# One-time setup
uv sync
source .venv/bin/activate
```

## Common Commands

### Building and Testing

```bash
# Build the provider binary (FlavorPack)
flavor pack

# Install to local Terraform plugin directory
# Binary goes to ~/.terraform.d/plugins/local/providers/pyvider/

# Run tests (via pyvider-components)
pytest

# Generate documentation
plating plate --output-dir docs
```

### Code Quality

After editing any Python file, run these commands:

```bash
# If `we` commands available:
we run format
we run lint
we run typecheck

# Otherwise:
ruff format <file>
ruff check --fix <file>
mypy <file>
```

### Local Testing with Terraform

```bash
# After building and installing
cd examples/<example_name>
terraform init
terraform plan
terraform apply
```

## Architecture

### Package Structure

This is a meta-package that brings together:
- **pyvider** - Core provider framework
- **pyvider-components** - Standard components (data sources, resources, functions)
- **flavorpack** - Binary packaging
- **plating** - Documentation generation
- **provide-foundation** - Logging and telemetry

### Component Discovery

Components are auto-discovered from `pyvider.components` package (configured in `pyproject.toml` under `[pyvider]`).

### FlavorPack Configuration

Configured in `pyproject.toml`:
- Entry point: `pyvider.cli:main`
- Output: `dist/terraform-provider-pyvider`
- Command name: `terraform-provider-pyvider`

### Local Installation Path

Provider installs to:
```
~/.terraform.d/plugins/local/providers/pyvider/<version>/{platform}/
└── terraform-provider-pyvider
```

Use in Terraform with:
```hcl
terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "<version>"
    }
  }
}
```

## Configuration Files

- `pyproject.toml` - Python project configuration, dependencies, tool settings
- `[pyvider]` section - Provider configuration, component packages
- `[tool.flavor]` - FlavorPack binary packaging settings

## Code Quality Standards

- Python version: 3.11+
- Uses provide-foundation for logging
- Components from pyvider-components

## Related Projects

Reference implementations and documentation:
- `pyvider` - Provider framework documentation
- `pyvider-components` - Component implementations
- `terraform-provider-tofusoup` - Another provider example
- `plating` - Documentation generation usage
- `flavorpack` - Binary packaging documentation

All located in `/Users/tim/code/gh/provide-io/`
