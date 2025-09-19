# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the official Terraform Provider for Pyvider, built entirely in Python using the Pyvider framework. It demonstrates the framework's capabilities and provides utility resources, data sources, and functions for testing and general infrastructure tasks.

The provider is packaged using the `flavorpack` toolchain which creates self-contained Python executables (.psp files) that include the Python runtime, all dependencies, and launcher binaries.

## Essential Commands

### Quick Start with Makefile
```bash
# Show all available commands
make help

# Common development workflow
make setup          # Set up environment
make build          # Build the provider
make test           # Test the provider
make docs           # Build documentation
make release        # Create a new release

# Version management
make bump-patch     # Bump patch version (0.0.3 -> 0.0.4)
make bump-minor     # Bump minor version (0.0.3 -> 0.1.0) 
make bump-major     # Bump major version (0.0.3 -> 1.0.0)

# Registry operations
make registry-check # Check Terraform Registry status
make registry-sync  # Sync with registry
```

### Manual Environment Setup
```bash
# Source the environment (if not using Makefile)
source env.sh

# The env.sh script automatically:
# - Installs UV package manager if needed
# - Creates/updates virtual environment in workenv/terraform-provider-pyvider_darwin_arm64/
# - Installs all dependencies including sibling packages (pyvider-components, pyvider-cty, etc.)
# - Sets up PYTHONPATH and activates the environment
```

### Building the Provider
```bash
# Build the provider package with architecture-specific naming
make build

# This creates both:
# - dist/terraform-provider-pyvider.psp (base PSP file)
# - dist/{platform}/terraform-provider-pyvider_v{version} (versioned binary)

# Platform detection:
# - darwin_arm64 (Apple Silicon Mac)
# - darwin_amd64 (Intel Mac)
# - linux_arm64 (ARM Linux)
# - linux_amd64 (x86_64 Linux)

# Build for all platforms (CI/CD reference):
make build-all

# The build process:
# - Creates a wheel from the current code
# - Downloads all transitive dependencies
# - Bundles Python runtime (3.11)
# - Signs the package with keys from keys/provider-private.key
# - Outputs to dist/terraform-provider-pyvider.psp (~84MB)
# - Copies to architecture-specific directory with versioned name
```

### Building Documentation
```bash
# Build documentation using plating (successor to garnish)
make docs

# Or run the build script directly:
./scripts/build-docs.sh

# This script:
# - Uses PlatingAPI to generate docs from pyvider-components code
# - Extracts examples from documentation to create .tf files
# - Generates conformance test configurations with tofusoup
# - Outputs documentation to docs/ directory
# - Creates examples in examples/ directory
# - Generates conformance tests in tests/conformance/

# Install documentation tools if needed
cd ../plating && uv pip install -e .
cd ../tofusoup && uv pip install -e .
```

### Migration from Garnish to Plating

**IMPORTANT**: This project has migrated from `garnish` to `plating` for documentation generation.

- **Garnish**: Deprecated documentation system (no longer used)
- **Plating**: New documentation generation system using PlatingAPI
- All scripts, Makefile targets, and CI/CD workflows now use plating
- PlatingAPI provides programmatic access to documentation generation

### Testing the Provider
```bash
# Test the provider executable (tests both PSP and versioned binary)
make test

# Test with Terraform locally
make test-local

# Run comprehensive plating tests
make test-plating

# Test example configurations
make test-examples

# The make test command runs:
# - Cold/warm start tests on the PSP file
# - Cold/warm start tests on the versioned binary
# - Performance timing for both variants

# The test-plating script:
# - Generates documentation using PlatingAPI
# - Builds and installs the provider automatically
# - Creates comprehensive Terraform test configurations
# - Runs full terraform init/plan/apply cycle
# - Generates detailed test reports
```

### Key Generation
```bash
# Generate signing keys using flavor (Ed25519 keys)
flavor keygen --out-dir keys

# Alternative: Generate RSA keys manually (if flavor keygen unavailable)
openssl genpkey -algorithm RSA -out keys/provider-private.key -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in keys/provider-private.key -out keys/provider-public.key
```

**Note**: The provider signing keys in `keys/` are temporary and throwaway. They're regenerated for each build in CI/CD.

### Cleanup Procedures

The Makefile provides comprehensive cleanup targets:

```bash
# Clean build artifacts and cache
make clean

# Clean documentation
make clean-docs

# Clean plating test outputs
make clean-plating

# Clean example test outputs
make clean-examples

# Clean all Terraform state files
make clean-tfstate

# Clean Terraform plugin cache
make clean-tfcache

# Clean flavor work environments
make clean-workenv

# Nuclear option - clean everything including venv
make clean-all
```

### Provider Binary Naming Conventions

Following HashiCorp's official Terraform Provider naming standards:

**Archive naming**: `terraform-provider-{NAME}_{VERSION}_{OS}_{ARCH}.zip`
- Example: `terraform-provider-pyvider_0.1.0_darwin_arm64.zip`

**Binary naming inside archive**: `terraform-provider-{NAME}_v{VERSION}`
- Example: `terraform-provider-pyvider_v0.1.0`
- Note: Binary has 'v' prefix, archive does not

**Local development structure**:
```
dist/
├── terraform-provider-pyvider.psp          # Base PSP file
├── darwin_arm64/
│   └── terraform-provider-pyvider_v0.0.5   # Versioned binary
├── darwin_amd64/
│   └── terraform-provider-pyvider_v0.0.5
├── linux_arm64/
│   └── terraform-provider-pyvider_v0.0.5
└── linux_amd64/
    └── terraform-provider-pyvider_v0.0.5
```

**Terraform plugin directory**:
```
~/.terraform.d/plugins/local/providers/pyvider/{VERSION}/{PLATFORM}/terraform-provider-pyvider
```

This architecture-specific structure prevents binary collisions when multiple architectures share a directory.

## Architecture and Structure

### Package Structure
This is a **meta-package** that brings together multiple Pyvider components:
- **pyvider**: Core framework for building Terraform providers in Python
- **pyvider-components**: Pre-built resources, data sources, and functions
- **pyvider-cty**: CTY type system implementation for Terraform compatibility  
- **pyvider-hcl**: HCL parsing and generation
- **pyvider-rpcplugin**: Terraform RPC plugin protocol implementation
- **pyvider-telemetry**: Structured logging and telemetry

### Key Configuration Files

**pyproject.toml**: Defines the package metadata, dependencies, and flavorpack build configuration
- Entry point: `pyvider.cli:main`
- Tool configuration under `[tool.flavor]` section
- Signing keys configured at `keys/provider-private.key` and `keys/provider-public.key`

**pyvider.toml**: Provider-specific configuration
- Specifies which component modules to load: `components = ["pyvider.components"]`

**terraform-registry-manifest.json**: Terraform registry metadata
- Declares protocol version 6.0 support

### Build System

The project uses **flavorpack** (flavor) for packaging:
- Creates self-contained executable packages (.psp files)
- Includes Python runtime, avoiding dependency on system Python
- Uses Rust launcher for fast startup
- Supports multiple platforms (darwin_arm64, darwin_amd64, linux_arm64, linux_amd64)

### Runtime Environment

When executed, the provider:
1. Extracts itself to `~/Library/Caches/flavor/workenv/terraform-provider-pyvider/` (on macOS)
2. Sets up isolated Python environment with all dependencies
3. Passes through Terraform environment variables (TF_*, PLUGIN_*)
4. Runs the `pyvider.cli:main` entry point

### Development Workflow

1. **Always start with**: `make setup` or `source env.sh` to set up the development environment
2. **Make code changes** in sibling pyvider packages if needed
3. **Build**: Run `make build` to create both PSP and versioned binary
4. **Install**: Run `make install` to install provider locally for Terraform
5. **Test**: Run `make test` to test both PSP and versioned binary performance
6. **Validate**: Run `make test-local` to test with actual Terraform configurations
7. **Documentation**: Run `make docs` to regenerate documentation with plating
8. **Clean**: Use appropriate `make clean-*` targets as needed

### Important Development Notes

- The project now uses **plating** instead of garnish for documentation generation
- Provider binaries are created in architecture-specific directories to prevent collisions
- Both PSP and versioned binaries are tested for performance comparisons
- Local installation follows Terraform's plugin directory structure
- Cleanup targets are comprehensive and prevent workspace pollution
- Platform detection is automatic based on `uname -s` and `uname -m`

## GitHub Actions Release Process

### Creating a Release

Releases are created via GitHub Actions using the **Build and Release** workflow:

1. Go to Actions → Build and Release → Run workflow
2. Enter version (e.g., `0.1.0`) and optionally mark as pre-release
3. The workflow will:
   - Build PSP packages for all platforms (linux_amd64, linux_arm64, darwin_amd64, darwin_arm64)
   - Test execution with `--launch-context` (timed for cold and warm starts)
   - Package as `terraform-provider-pyvider_{VERSION}_{OS}_{ARCH}.zip`
   - Generate SHA256SUMS with all files including manifest
   - GPG sign the SHA256SUMS file (binary signature format)
   - Create GitHub release with all artifacts

### Required GitHub Secrets

Configure these secrets in repository settings:

- **GPG_PRIVATE_KEY**: Exported GPG private key (ASCII armored)
  ```bash
  gpg --armor --export-secret-keys <secrety key>
  ```
- **GPG_PASSPHRASE**: Passphrase for the GPG key (if applicable)
- **GPG_KEY_ID**: `<sercret key>``

### Local GPG Signing

For manual signing of release artifacts:
```bash
# Sign a file (creates binary signature, not ASCII armored)
gpg --detach-sign --local-user <secret key> terraform-provider-pyvider_0.1.0_SHA256SUMS

# Verify signature
gpg --verify terraform-provider-pyvider_0.1.0_SHA256SUMS.sig terraform-provider-pyvider_0.1.0_SHA256SUMS
```

### Release Artifacts

Each release includes:
- `terraform-provider-pyvider_{VERSION}_{OS}_{ARCH}.zip` - Provider binary archives
- `terraform-provider-pyvider_{VERSION}_manifest.json` - Terraform Registry manifest
- `terraform-provider-pyvider_{VERSION}_SHA256SUMS` - Checksums for all files
- `terraform-provider-pyvider_{VERSION}_SHA256SUMS.sig` - GPG signature (binary format)

## Important Notes

- The `workenv/` directory should be ignored - it's the local development virtual environment
- The provider requires Python 3.11+ for development but bundles its own runtime
- Signing keys in `keys/` are temporary/throwaway - regenerated for each build
- The built .psp file is completely self-contained and portable
- GitHub Actions workflows handle multi-platform builds and releases
- GPG signatures use binary format (not ASCII armored) for Terraform Registry compatibility

## Troubleshooting

### Common Issues and Solutions

**Import errors during build**:
```bash
# Fix with local workspace package installation
uv pip install -e '../provide-foundation[all]'
uv pip install -e '../pyvider-components'
uv pip install -e '../plating'
```

**Provider not found by Terraform**:
```bash
# Ensure provider is built and installed
make build
make install
# Check installation location
ls -la ~/.terraform.d/plugins/local/providers/pyvider/
```

**Stale cache issues**:
```bash
# Clean flavor work environments
make clean-workenv
# Or manually remove cache
rm -rf ~/Library/Caches/flavor/workenv/terraform-provider-pyvider*
```

**Performance testing**:
```bash
# Compare cold vs warm start times
make test
# First run extracts and sets up environment (~3.3s)
# Second run uses cached environment (~0.14s)
```

### Migration from Garnish

If you encounter references to `garnish`:
1. Replace all `garnish` commands with `plating` equivalents
2. Use `PlatingAPI` instead of garnish CLI commands
3. Update import statements to use plating modules
4. Check CI/CD workflows for garnish references

The migration ensures consistent documentation generation and removes dependency on deprecated tools.