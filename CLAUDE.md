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
# Build the provider package (.psp file)
flavor pack

# The build process:
# - Creates a wheel from the current code
# - Downloads all transitive dependencies
# - Bundles Python runtime (3.11)
# - Signs the package with keys from keys/provider-private.key
# - Outputs to dist/terraform-provider-pyvider.psp (~84MB)
```

### Building Documentation
```bash
# Build documentation for pyvider-components
./scripts/build-docs.sh

# This script:
# - Uses garnish to generate docs from pyvider-components code
# - Extracts examples from documentation to create .tf files
# - Generates conformance test configurations with tofusoup
# - Outputs documentation to docs/ directory
# - Creates examples in examples/ directory
# - Generates conformance tests in tests/conformance/

# Install documentation tools if needed
uv tool install garnish
uv tool install tofusoup
```

### Testing the Provider
```bash
# Test the provider executable
./dist/terraform-provider-pyvider.psp provide --help

# Run local build test script (includes platform detection)
./test-build-local.sh
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

1. **Always start with**: `source env.sh` to set up the development environment
2. **Make code changes** in sibling pyvider packages if needed
3. **Build**: Run `flavor pack` to create the provider package
4. **Test**: Execute the built package or use with Terraform
5. **Clean cache**: If needed, remove `~/Library/Caches/flavor/workenv/terraform-provider-pyvider/`

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