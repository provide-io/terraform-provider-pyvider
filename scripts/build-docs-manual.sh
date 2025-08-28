#!/bin/bash
# Manual documentation builder for terraform-provider-pyvider
# Creates basic documentation structure when garnish is not working

set -euo pipefail

# Colors for output
COLOR_BLUE='\033[0;34m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'
COLOR_RED='\033[0;31m'
COLOR_NC='\033[0m'

echo -e "${COLOR_BLUE}📚 Building documentation structure manually...${COLOR_NC}"

DOCS_DIR="docs"

# Clean and create directories
rm -rf $DOCS_DIR/*
mkdir -p $DOCS_DIR/{resources,data-sources,functions}

# Create index
cat > $DOCS_DIR/index.md << 'EOF'
---
page_title: "pyvider Provider"
description: |-
  The official Pyvider provider for Terraform/OpenTofu
---

# pyvider Provider

The `pyvider` provider is the official provider for the Pyvider framework, demonstrating Python-based Terraform provider development.

## Example Usage

```hcl
terraform {
  required_providers {
    pyvider = {
      source  = "provide-io/pyvider"
      version = "~> 0.0"
    }
  }
}

provider "pyvider" {
  # Configuration options
}
```

## Resources

- `pyvider_file_content` - Manages file content
- `pyvider_local_directory` - Manages local directories
- `pyvider_timed_token` - Creates time-limited tokens
- `pyvider_private_state_verifier` - Verifies private state
- `pyvider_warning_example` - Example resource with warnings

## Data Sources

- `pyvider_env_variables` - Read environment variables
- `pyvider_file_info` - Get file information
- `pyvider_provider_config_reader` - Read provider configuration
- `pyvider_jq` - Process data with JQ queries
- `pyvider_jq_cty` - JQ with CTY type handling

## Functions

Provider includes various utility functions for string manipulation, numeric operations, and collection handling.
EOF

# Create placeholder resource docs
cat > $DOCS_DIR/resources/file_content.md << 'EOF'
---
page_title: "pyvider_file_content Resource"
description: |-
  Manages file content on the local filesystem
---

# pyvider_file_content

Manages file content on the local filesystem.

## Example Usage

```hcl
resource "pyvider_file_content" "example" {
  path    = "/tmp/example.txt"
  content = "Hello, World!"
}
```

## Argument Reference

- `path` - (Required) The file path
- `content` - (Required) The file content

## Attribute Reference

- `id` - The file path
- `exists` - Whether the file exists
EOF

# Create placeholder data source docs
cat > $DOCS_DIR/data-sources/env_variables.md << 'EOF'
---
page_title: "pyvider_env_variables Data Source"
description: |-
  Read environment variables
---

# pyvider_env_variables

Reads environment variables from the system.

## Example Usage

```hcl
data "pyvider_env_variables" "path" {
  keys = ["PATH", "HOME"]
}

output "path" {
  value = data.pyvider_env_variables.path.values["PATH"]
}
```

## Argument Reference

- `keys` - (Required) List of environment variable names to read

## Attribute Reference

- `values` - Map of environment variable names to their values
EOF

# Create placeholder function docs
cat > $DOCS_DIR/functions/upper.md << 'EOF'
---
page_title: "upper Function"
description: |-
  Convert string to uppercase
---

# upper Function

Converts a string to uppercase.

## Example Usage

```hcl
output "uppercase" {
  value = provider::pyvider::upper("hello")
}
```

## Signature

```
upper(string) string
```

## Arguments

1. `string` - The string to convert

## Return Value

The uppercase version of the input string.
EOF

echo -e "${COLOR_GREEN}✅ Basic documentation structure created${COLOR_NC}"
echo "  Resources: $(ls -1 $DOCS_DIR/resources/*.md 2>/dev/null | wc -l)"
echo "  Data Sources: $(ls -1 $DOCS_DIR/data-sources/*.md 2>/dev/null | wc -l)"
echo "  Functions: $(ls -1 $DOCS_DIR/functions/*.md 2>/dev/null | wc -l)"