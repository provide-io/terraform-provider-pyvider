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

#### For Development Builds (Testing Local Changes)

**IMPORTANT**: When developing and testing changes to pyvider packages, you do NOT need to rebuild or reinstall the provider package each time. The `pyvider install` command creates a **persistent wrapper script** that uses your virtual environment.

**Fast iteration workflow**:
```bash
# 1. Initial setup (one-time)
make setup                    # Or: source env.sh
pyvider install              # Creates wrapper script pointing to your venv

# 2. Make code changes to pyvider packages
cd ../pyvider && vim src/pyvider/...
cd ../pyvider-components && vim src/pyvider/components/...

# 3. Install changes to venv (NO rebuild needed!)
cd ../pyvider && uv pip install -e .
cd ../pyvider-components && uv pip install -e .

# 4. Test immediately
cd /path/to/test && terraform plan

# The wrapper script automatically uses the updated venv code!
```

**When you DO need to reinstall**:
- Only if you change the venv location/path
- Only if the wrapper script gets deleted
- NOT needed for code changes to pyvider packages

**How it works**:
- `pyvider install` creates: `~/.terraform.d/plugins/local/providers/pyvider/0.1.0/darwin_arm64/terraform-provider-pyvider`
- This is a bash wrapper script that:
  - Activates your project's `.venv`
  - Runs `pyvider provide` command
  - Uses whatever code is currently installed in that venv
- Changes to pyvider packages are immediately available after `uv pip install -e .`

#### For Production Builds (PSP Packages)

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

### Smart Variadic Parameters Implementation

Pyvider supports **Smart Variadic Parameters** for provider functions, enabling true optional parameters with excellent developer experience.

#### How It Works

Functions can declare variadic parameters using Python's `*args` syntax:

```python
# In pyvider-components/src/pyvider/components/functions/numeric_functions.py
@register_function(
    summary="Round a number",
    return_type=Number,
    parameters=[
        ParameterMeta(
            name="number",
            description="The number to round",
            type=Number,
        ),
    ]
)
def round_number(number: float, *options) -> int | float:
    """Round a number to specified precision."""
    precision = options[0] if options else 0
    return round(number, precision)
```

#### Usage in Terraform

```hcl
# Without optional parameter (uses default)
output "rounded" {
  value = provider::pyvider::round(3.14159)  # → 3
}

# With optional parameter
output "precise" {
  value = provider::pyvider::round(3.14159, 2)  # → 3.14
}

# String functions with options
output "camelCase" {
  value = provider::pyvider::to_camel_case("my_var")      # → "myVar"
}

output "PascalCase" {
  value = provider::pyvider::to_camel_case("my_var", true) # → "MyVar"
}
```

#### Implementation Details

The variadic parameter system consists of three key components:

**1. Schema Generation** (`pyvider/src/pyvider/functions/adapters.py`):
- `_extract_parameters_meta()` detects `*args` (VAR_POSITIONAL) parameters
- Returns separate `parameters` (required) and `variadic_parameter` (optional)
- Provides metadata for both to the protocol layer

**2. Protocol Conversion** (`pyvider/src/pyvider/protocols/tfprotov6/adapters/function_adapter.py`):
- `dict_to_proto_function()` includes `variadic_parameter` in protobuf Function message
- Terraform protocol 6.0 natively supports variadic parameters

**3. Function Invocation** (`pyvider/src/pyvider/protocols/tfprotov6/handlers/call_function.py`):
- `_process_function_arguments()` handles variadic parameters from extra request arguments
- Extracts variadic args beyond required parameters and places in tuple
- `_invoke_function()` builds positional args in signature order:
  - Required parameters → positional_args (in declaration order)
  - Variadic parameters → variadic_args (from *args tuple)
  - Combined as: `function(*positional_args, *variadic_args)`
  - This prevents "multiple values for parameter" errors

#### Key Technical Points

**Parameter Ordering Fix**: The critical fix in `_invoke_function()` ensures proper argument ordering:

```python
# Build arguments in signature order
positional_args = []      # Required params in order
variadic_args = []        # Optional variadic params

for param_name, param in func_sig.parameters.items():
    if param.kind == inspect.Parameter.VAR_POSITIONAL:
        variadic_args = native_kwargs[param_name]
    elif param.kind in (...POSITIONAL...):
        positional_args.append(native_kwargs[param_name])

# Combine and invoke
all_args = positional_args + list(variadic_args)
result = function_obj(*all_args)  # Correct call!
```

**Without this fix**: `round(number=3.14, *(2,))` → Error: multiple values for 'number'
**With this fix**: `round(3.14, 2)` → Success: 3.14

#### Benefits

✅ **True optional parameters** - no need for null sentinels or required defaults
✅ **Clean syntax** - `round(3.14, 2)` vs `round(3.14, null, 2)`
✅ **Better DX** - parameters are genuinely optional, not just nullable
✅ **Type safety** - variadic args are properly typed and validated
✅ **Native Terraform** - uses protocol 6.0 variadic parameter support

#### Functions Using Variadic Parameters

Current functions with smart variadic parameters:
- `round(number, *options)` - optional precision parameter
- `to_camel_case(text, *options)` - optional upper_first parameter
- `format_size(size_bytes, *options)` - optional precision parameter
- `truncate_text(text, *options)` - optional max_length and suffix parameters
- `pluralize_word(word, *options)` - optional count and plural parameters

#### Testing Variadic Functions

```bash
# Create test configuration
cat > test.tf << 'EOF'
terraform {
  required_providers {
    pyvider = { source = "local/providers/pyvider" }
  }
}

output "test_with_option" {
  value = provider::pyvider::round(3.14159, 2)  # → 3.14
}

output "test_without_option" {
  value = provider::pyvider::round(3.14159)     # → 3
}
EOF

# Test
terraform init && terraform plan
```

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