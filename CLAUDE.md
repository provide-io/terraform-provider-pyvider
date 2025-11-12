# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`terraform-provider-pyvider` is a proof-of-concept Terraform provider demonstrating the Pyvider framework's capabilities for building Terraform providers in Python. It showcases how to use `pyvider` to create providers that are compatible with Terraform's plugin protocol.

## Task Runner

This project uses `wrknv` for task automation. Commands are defined in `wrknv.toml`.

### Quick Reference
```bash
we tasks          # List all available tasks
we test           # Run tests
we lint           # Check code quality
we format         # Format code
we typecheck      # Type checking
we build          # Build package
```

All tasks can be run with `we <task>`. Nested tasks use spaces (e.g., `we test coverage`).

### Task Discovery

Run `we tasks` to see the complete task tree for this project. Common task hierarchies:

```bash
we test                # Run all tests
we test coverage       # Run tests with coverage
we test parallel       # Run tests in parallel
```

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync
```

### Primary Workflow (using we)
```bash
# Testing
we test                    # Run all tests
we test coverage           # Run with coverage report
we test parallel           # Run tests in parallel

# Code quality
we lint                    # Check code quality
we lint fix                # Auto-fix linting issues
we format                  # Format code
we format check            # Check formatting without changes
we typecheck               # Run type checker

# Building
we build                   # Build distribution
```

### Alternative (Direct Commands)
```bash
# Testing
uv run pytest                      # Direct test execution
uv run pytest -n auto              # Run tests in parallel
uv run pytest --cov=terraform_provider_pyvider  # Run with coverage

# Code quality
uv run ruff format                 # Format code
uv run ruff check                  # Lint code
uv run ruff check --fix            # Auto-fix linting issues
uv run mypy src/                   # Type checking
```

For complete task documentation, see [wrknv.toml](wrknv.toml) or run `we tasks`.

## Architecture

This provider serves as a proof-of-concept demonstrating:
- **Pyvider Framework Integration**: How to build providers using Python
- **Terraform Plugin Protocol v6**: Compliance with Terraform's plugin protocol
- **Resource & Data Source Implementation**: Examples of implementing Terraform resources and data sources in Python

## Development Guidelines

- Always use modern Python 3.11+ type hints (e.g., `list[str]` not `List[str]`)
- Follow existing code patterns in the pyvider framework
- Test changes against actual Terraform/OpenTofu configurations
- Use `provide.foundation` for structured logging

## Testing

Run tests with:
```bash
we test
```

For testing with actual Terraform configurations, see the `examples/` directory.
