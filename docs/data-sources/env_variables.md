---
page_title: "Data Source: pyvider_env_variables"
description: |-
  Provides access to environment variables with filtering and transformation capabilities
---
# pyvider_env_variables (Data Source)

The `pyvider_env_variables` data source allows you to access environment variables from the system where Terraform is running. It provides flexible filtering by keys, prefixes, or regex patterns, plus built-in transformations for keys and values.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


This data source enables dynamic, environment-aware infrastructure configurations by bridging the gap between your system environment and Terraform resources. Whether you're managing multi-environment deployments, integrating with CI/CD pipelines, or implementing configuration-as-code patterns, this data source provides the flexibility to access and transform environment state seamlessly.

## Capabilities

This data source enables you to:

- **Configuration management**: Read environment-specific settings and inject them into your infrastructure
- **Multi-environment deployments**: Access different configurations per environment without hardcoding values
- **Secrets injection**: Pull sensitive values from environment variables with proper sensitivity handling
- **Dynamic configuration**: Use environment state to influence resource creation and configuration decisions
- **CI/CD integration**: Access build and deployment variables from your automation pipelines
- **Flexible filtering**: Filter variables by specific keys, prefixes, or regex patterns
- **Value transformation**: Transform both keys and values (case conversion) before use
- **Sensitive data handling**: Mark specific variables as sensitive to prevent exposure in logs and outputs

## Example Usage

```terraform
data "pyvider_env_variables" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_env_variables"
  value       = data.pyvider_env_variables.example
  sensitive   = true
}

```

## Examples

Explore these examples to see the data source in action:

- **[example.tf](examples/example.tf)** - Basic environment variable access
- **[basic.tf](examples/basic.tf)** - Simple variable reading with specific keys
- **[filtering.tf](examples/filtering.tf)** - Advanced filtering with prefix and regex patterns
- **[advanced.tf](examples/advanced.tf)** - Complex transformations and case-sensitivity controls
- **[multi_environment.tf](examples/multi_environment.tf)** - Multi-environment configuration patterns
- **[comprehensive.tf](examples/comprehensive.tf)** - Complete feature demonstration

## Argument Reference



## Filtering Options

The data source provides multiple ways to filter environment variables:

| Filter Type | Parameter | Description | Example |
|------------|-----------|-------------|---------|
| **Specific Keys** | `keys` | List of exact variable names to retrieve | `["PATH", "HOME", "USER"]` |
| **Prefix** | `prefix` | Match variables starting with a string | `"MYAPP_"` matches `MYAPP_DATABASE_URL` |
| **Regex** | `regex` | Match variables with a regex pattern | `".*_URL$"` matches variables ending in `_URL` |

## Transformations

### Key Transformations

Transform variable names before returning using the `transform_keys` parameter:

- `"lower"` - Convert keys to lowercase
- `"upper"` - Convert keys to uppercase

### Value Transformations

Transform variable values using the `transform_values` parameter:

- `"lower"` - Convert values to lowercase
- `"upper"` - Convert values to uppercase

### Case Sensitivity

Control case-sensitive matching with the `case_sensitive` parameter (defaults to `true`).

## Output Attributes

| Attribute | Type | Sensitivity | Description |
|-----------|------|-------------|-------------|
| `values` | map(string) | Non-sensitive only | Non-sensitive variables as a map |
| `sensitive_values` | map(string) | Sensitive | Variables marked as sensitive via `sensitive_keys` |
| `all_values` | map(string) | Sensitive if any | All variables combined (marked sensitive if any are) |
| `all_environment` | map(string) | Varies | Complete environment snapshot |

## Related Components

- **pyvider_file_content** (Resource) - Write environment-based configuration files to disk
- **pyvider_provider_config_reader** (Data Source) - Access provider configuration values
- **pyvider_http_api** (Data Source) - Fetch configuration from external APIs