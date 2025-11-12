# Terraform Provider: Pyvider

> **⚠️ Proof of Concept:** This is a proof-of-concept Terraform provider demonstrating what's possible when building providers in Python using the pyvider framework. Use it to learn Python-based provider development or to access utility resources for testing and diagnostics—but not for production infrastructure.

**What it is:** A working Terraform provider that bundles a representative set of example resources, data sources, and functions—built entirely in Python.

**What it does:** Provides utilities for file management, environment diagnostics, data transformation (jq), and infrastructure testing.

**Why it matters:** Proves you can build fully functional Terraform providers in Python instead of Go, and serves as a reference implementation for the [pyvider framework](https://github.com/provide-io/pyvider).

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

## Features

* **Utility Resources:** Manage local files and directories (`pyvider_file_content`, `pyvider_local_directory`).
* **Diagnostic Data Sources:** Inspect the provider's environment (`pyvider_env_variables`), read local file metadata (`pyvider_file_info`), and test provider configuration (`pyvider_provider_config_reader`).
* **Powerful Data Transformation:** Process JSON and other data structures using `jq` queries directly within your Terraform configuration (`pyvider_lens_jq`).
* **Extensive Function Library:** A rich set of functions for string manipulation, numeric operations, and collection handling.

## Relationship to pyvider-components

This provider is built using components from the [pyvider-components](https://github.com/provide-io/pyvider-components) repository, which serves as the reference implementation and example library for the Pyvider framework.

**Key Relationship:**
- **pyvider-components**: Example library for learning provider development (this provider uses a curated subset)
- **terraform-provider-pyvider**: Proof-of-concept provider that packages those components for Terraform testing and learning

```
pyvider-components (examples) ──packages──> terraform-provider-pyvider (POC/testing)
```

**Why two repositories?**
- **pyvider-components** is for developers building their own providers (learning/reference)
- **terraform-provider-pyvider** is for learning and testing the provider in Terraform (proof-of-concept)

**Building your own provider?** Start with [pyvider-components](https://github.com/provide-io/pyvider-components) to see working examples, then use the [pyvider framework](https://github.com/provide-io/pyvider) to build your custom provider.

## Getting Started

**New to the pyvider provider?** Check out our comprehensive tutorial:

**[→ Getting Started Tutorial](docs/guides/02-getting-started.md)** - Complete walkthrough in 10-15 minutes

The tutorial covers:
- Installing and configuring the provider
- Creating your first resources
- Using data sources
- Updating and destroying resources

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
      version = ">= 0.0.0"  # For development: accepts any version
      # For production, pin to specific version: version = "~> 0.1"
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

## Development

### Quick Start

```bash
# Set up environment
uv sync

# Run common tasks
we test           # Run tests
we lint           # Check code
we format         # Format code
we tasks          # See all available commands
```

### Available Commands

This project uses `wrknv` for task automation. Run `we tasks` to see all available commands.

**Common tasks:**
- `we test` - Run all tests
- `we test coverage` - Run tests with coverage
- `we test parallel` - Run tests in parallel
- `we lint` - Check code quality
- `we lint fix` - Auto-fix linting issues
- `we format` - Format code
- `we typecheck` - Run type checker

See [CLAUDE.md](CLAUDE.md) for detailed development instructions and architecture information.
