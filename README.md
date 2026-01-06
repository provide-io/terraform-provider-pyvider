# Terraform Provider: Pyvider

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package_manager-FF6B35.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/provide-io/terraform-provider-pyvider/actions/workflows/ci.yml/badge.svg)](https://github.com/provide-io/terraform-provider-pyvider/actions)

> **Initial release:** This Terraform provider demonstrates what's possible when building providers in Python using the pyvider framework, and includes a representative set of resources, data sources, and functions.

**What it is:** A working Terraform provider that bundles a representative set of example resources, data sources, and functions—built entirely in Python.

**What it does:** Provides utilities for file management, environment diagnostics, data transformation (jq), and infrastructure testing.

**Why it matters:** Proves you can build fully functional Terraform providers in Python instead of Go, and serves as a reference implementation for the [pyvider framework](https://github.com/provide-io/pyvider).

## Features

* **Utility Resources:** Manage local files and directories (`pyvider_file_content`, `pyvider_local_directory`).
* **Diagnostic Data Sources:** Inspect the provider's environment (`pyvider_env_variables`), read local file metadata (`pyvider_file_info`), and test provider configuration (`pyvider_provider_config_reader`).
* **Powerful Data Transformation:** Process JSON and other data structures using `jq` queries directly within your Terraform configuration (`pyvider_lens_jq`).
* **Extensive Function Library:** A rich set of functions for string manipulation, numeric operations, and collection handling.

## Getting Started

> **Note**: terraform-provider-pyvider is in pre-release (v0.x.x). APIs and features may change before 1.0 release.

**New to the pyvider provider?** Check out our comprehensive tutorial:

**[→ Getting Started Tutorial](https://github.com/provide-io/terraform-provider-pyvider/blob/main/docs/guides/getting-started.md)** - Complete walkthrough in 10-15 minutes

The tutorial covers:
- Installing and configuring the provider
- Creating your first resources
- Using data sources
- Updating and destroying resources

## Documentation
- [Documentation index](https://github.com/provide-io/terraform-provider-pyvider/blob/main/docs/index.md)
- [Getting started](https://github.com/provide-io/terraform-provider-pyvider/blob/main/docs/guides/getting-started.md)
- [Examples](https://github.com/provide-io/terraform-provider-pyvider/tree/main/examples)

## Development

### Quick Start

```bash
# Set up environment
uv sync

# Run common tasks
we run test       # Run tests
we run lint       # Check code
we run format     # Format code
we tasks          # See all available commands
```

### Available Commands

This project uses `wrknv` for task automation. Run `we tasks` to see all available commands.

**Common tasks:**
- `we run test` - Run all tests
- `we run test.coverage` - Run tests with coverage
- `we run test.parallel` - Run tests in parallel
- `we run lint` - Check code quality
- `we run lint.fix` - Auto-fix linting issues
- `we run format` - Format code
- `we typecheck` - Run type checker

See [CLAUDE.md](https://github.com/provide-io/terraform-provider-pyvider/blob/main/CLAUDE.md) for detailed development instructions and architecture information.

## Contributing
See [CLAUDE.md](https://github.com/provide-io/terraform-provider-pyvider/blob/main/CLAUDE.md) for contribution guidance.

## License
See [LICENSE](https://github.com/provide-io/terraform-provider-pyvider/blob/main/LICENSE) for license details.

## When to Use This Provider

**✅ Use this provider for:**
- Learning how to build Terraform providers in Python
- Studying working examples of provider patterns
- Quick testing and diagnostic utilities
- Proof-of-concept work
- Understanding the pyvider framework capabilities

**❌ Don't use this provider for:**
- Production infrastructure management (build a custom provider instead)
- Critical systems or workflows
- Long-term production configurations

**For production needs:** Build your own custom provider using [pyvider](https://github.com/provide-io/pyvider), or use established providers (AWS, Azure, etc.).

## Relationship to pyvider-components

This provider is built using components from the [pyvider-components](https://github.com/provide-io/pyvider-components) repository, which serves as the reference implementation and example library for the Pyvider framework.

**Key Relationship:**
- **pyvider-components**: Example library for learning provider development (this provider uses a curated subset)
- **terraform-provider-pyvider**: Proof-of-concept provider that packages those components for Terraform testing and learning

```
pyvider-components (examples) ──packages──> terraform-provider-pyvider (pre-release/testing)
```

**Why two repositories?**
- **pyvider-components** is for developers building their own providers (learning/reference)
- **terraform-provider-pyvider** is for learning and testing the provider in Terraform (pre-release)

**Building your own provider?** Start with [pyvider-components](https://github.com/provide-io/pyvider-components) to see working examples, then use the [pyvider framework](https://github.com/provide-io/pyvider) to build your custom provider.

## Installation

1. **Download:** Download the appropriate `terraform-provider-pyvider` binary for your system from the releases page.
2. **Install:** Run the downloaded binary with the `install` command. It will automatically copy itself to the correct Terraform plugin directory.

    ```sh
    ./terraform-provider-pyvider install
    ```

## Example Usage

Configure the provider in your Terraform code. Most resources and data sources work without additional provider configuration.

```hcl
terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.3"
    }
  }
}

provider "pyvider" {
  # No configuration needed for most resources/data sources
}

# Use a data source from the provider
data "pyvider_env_variables" "path" {
  keys = ["PATH"]
}

output "path_env" {
  value = data.pyvider_env_variables.path.values["PATH"]
}
```

Copyright (c) provide.io LLC.
