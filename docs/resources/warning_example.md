---
page_title: "Resource: pyvider_warning_example"
subcategory: "Test Mode"
description: |-
  Demonstrates Terraform warning mechanisms for deprecated attributes and validation
---
# pyvider_warning_example (Resource)

The `pyvider_warning_example` resource is designed to demonstrate how Terraform providers can issue warnings for deprecated attributes, configuration conflicts, and validation scenarios. This resource is primarily used for testing warning mechanisms during provider development and for educational purposes.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


This resource showcases Terraform's built-in warning capabilities, demonstrating how providers can guide users through API migrations, deprecate old attributes, and validate configurations with helpful warnings rather than hard errors. It's an invaluable tool for provider developers learning to implement graceful deprecation paths and for users understanding how Terraform communicates configuration guidance.

## Capabilities

This resource enables you to:

- **Provider development**: Test and implement warning mechanisms in Terraform providers
- **Educational purposes**: Learn and demonstrate how Terraform warnings work in practice
- **Migration testing**: Test deprecated attribute warnings during API version transitions
- **Validation testing**: Test configuration validation and warning scenarios
- **Documentation examples**: Provide clear examples of warning patterns in provider docs
- **Deprecation paths**: Demonstrate graceful migration paths for deprecated attributes
- **Configuration validation**: Show how to validate mutually exclusive or conflicting attributes

## Example Usage

```terraform
resource "pyvider_warning_example" "example" {
  name = "example_warning"
}

output "example_name" {
  description = "The name of the pyvider_warning_example resource"
  value       = pyvider_warning_example.example.name
}

```

## Examples

Explore these examples to see the resource in action:

- **[example.tf](examples/example.tf)** - Basic warning demonstration and configuration patterns

## Argument Reference



## Warning Mechanisms

The resource demonstrates several types of Terraform warnings:

### 1. Deprecated Attribute Warnings

When using the `old_name` attribute, Terraform will issue a deprecation warning:
```
Warning: Attribute 'old_name' is deprecated
Please use the 'name' attribute instead.
```

### 2. Configuration Validation Warnings

The resource validates configuration and issues warnings for:
- Mutually exclusive attributes (`name` and `source_file`)
- Missing required configuration (all attributes empty)

### 3. Migration Path Warnings

Demonstrates how to guide users through attribute migrations and API changes gracefully.

## Attribute Behavior

### Configuration Logic

| Attribute | Purpose | Warning Behavior |
|-----------|---------|------------------|
| `name` | Primary attribute for resource name | No warnings (preferred) |
| `old_name` | Deprecated attribute | Triggers deprecation warning |
| `source_file` | Alternative file-based configuration | No warnings (valid alternative) |

### Validation Rules

1. `name` and `source_file` are mutually exclusive
2. At least one of `name`, `old_name`, or `source_file` must be specified
3. `old_name` triggers a deprecation warning when used

### Value Resolution Precedence

1. If `name` is specified: uses `name` value
2. If `old_name` is specified: uses `old_name` value (with warning)
3. If `source_file` is specified: uses `from_file:{source_file}` format

## Configuration Patterns

### Modern Configuration (No Warnings)

```terraform
resource "pyvider_warning_example" "modern" {
  name = "new-style-name"
}
```

### Deprecated Configuration (Triggers Warning)

```terraform
resource "pyvider_warning_example" "deprecated" {
  old_name = "legacy-style-name"
}
# Warning: Attribute 'old_name' is deprecated. Please use 'name' instead.
```

### File-Based Configuration

```terraform
resource "pyvider_warning_example" "file_based" {
  source_file = "config.yaml"
}
# Result: "from_file:config.yaml"
```

## Migration Scenario Testing

### Before Migration (Triggers Warning)

```terraform
resource "pyvider_warning_example" "before_migration" {
  old_name = "old-style-name"
}
```

### After Migration (No Warning)

```terraform
resource "pyvider_warning_example" "after_migration" {
  name = "new-style-name"
}
```

### Conditional Migration

```terraform
variable "use_legacy_config" {
  type    = bool
  default = false
}

resource "pyvider_warning_example" "conditional" {
  name     = var.use_legacy_config ? null : "modern-config"
  old_name = var.use_legacy_config ? "legacy-config" : null
}
```

## Testing Warning Mechanisms

### Multiple Configuration Methods

```terraform
# Method 1: Direct name (preferred)
resource "pyvider_warning_example" "direct" {
  name = "direct-configuration"
}

# Method 2: File-based configuration
resource "pyvider_warning_example" "file_based" {
  source_file = "config.yaml"
}

# Method 3: Legacy method (with warning)
resource "pyvider_warning_example" "legacy" {
  old_name = "legacy-style"
}
```

## Import

```bash
terraform import pyvider_warning_example.example <id>
```

## Related Components

- **pyvider_private_state_verifier** (Resource) - Verify private state encryption mechanisms
- **pyvider_simple_resource** (Resource) - Basic resource for comparison testing