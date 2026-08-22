---
page_title: "Data Source: pyvider_env_variables"
description: |-
  Provides access to environment variables with filtering and transformation capabilities
---
# pyvider_env_variables (Data Source)

The `pyvider_env_variables` data source allows you to access environment variables from the system where Terraform is running. It provides flexible filtering by keys, prefixes, or regex patterns, plus built-in transformations for keys and values.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


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

## More Examples

### Simple variable reading with specific keys

```terraform
# Read a specific environment variable by key.
# Before running, export a variable: export MY_APP_USERNAME="admin"
data "pyvider_env_variables" "user" {
  keys = ["MY_APP_USERNAME"]
}

output "basic_username" {
  description = "The username read from the environment."
  value       = lookup(data.pyvider_env_variables.user.values, "MY_APP_USERNAME", "not_set")
}

```

### Advanced filtering with prefix and regex patterns

```terraform
# Environment variable filtering examples

# Filter by prefix with case-sensitive matching
data "pyvider_env_variables" "app_config" {
  prefix = "APP_"
}

# Complex regex patterns
data "pyvider_env_variables" "url_vars" {
  regex = ".*_URL$" # Matches any variable ending in _URL
}

data "pyvider_env_variables" "credential_vars" {
  regex = ".*(KEY|SECRET|TOKEN|PASSWORD).*" # Security-related variables
}

# Categorize variables by type
locals {
  filtering_variable_categories = {
    filtering_urls = {
      for k, v in data.pyvider_env_variables.url_vars.values : k => v
    }
    credentials = {
      for k, v in data.pyvider_env_variables.credential_vars.values : k => {
        length    = length(v)
        has_value = v != ""
      }
    }
  }
}

output "filtering_urls" {
  description = "Results of various filtering approaches"
  value = {
    app_config_count   = length(data.pyvider_env_variables.app_config.values)
    url_matches        = length(data.pyvider_env_variables.url_vars.values)
    credential_matches = length(data.pyvider_env_variables.credential_vars.values)
  }
}

```

### Complex transformations and case-sensitivity controls

```terraform
# Before running, export the following variables:
# export API_URL="https://api.example.com"
# export API_TOKEN="secret-token-value"
# export API_TIMEOUT="60"

# Read all variables with a common prefix
data "pyvider_env_variables" "api_config" {
  prefix         = "API_"
  case_sensitive = true
  sensitive_keys = ["API_TOKEN"]
}

output "advanced_api_endpoint" {
  description = "The API endpoint URL."
  value       = lookup(data.pyvider_env_variables.api_config.values, "API_URL", "https://default.example.com")
}

output "advanced_api_timeout" {
  description = "The configured API timeout."
  value       = lookup(data.pyvider_env_variables.api_config.values, "API_TIMEOUT", "30")
}

output "advanced_api_token_is_sensitive" {
  description = "Demonstrates that the token is in the sensitive_values map."
  value       = "The API token is present in the sensitive outputs."
  sensitive   = true
}

```

### Multi-environment configuration patterns

```terraform
# Multi-environment configuration

variable "environment" {
  type    = string
  default = "development"
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

# Read environment-specific variables
data "pyvider_env_variables" "env_config" {
  prefix = "${upper(var.environment)}_"
}

# Read common application variables
data "pyvider_env_variables" "app_common" {
  prefix = "APP_"
}

locals {
  # Environment-specific configuration with fallbacks
  multi_environment_database_url = lookup(
    data.pyvider_env_variables.env_config.values,
    "${upper(var.environment)}_DATABASE_URL",
    "postgres://localhost/${var.environment}"
  )

  api_url = lookup(
    data.pyvider_env_variables.env_config.values,
    "${upper(var.environment)}_API_URL",
    var.environment == "production" ? "https://api.example.com" : "http://localhost:3000"
  )

  log_level = lookup(
    data.pyvider_env_variables.env_config.values,
    "${upper(var.environment)}_LOG_LEVEL",
    var.environment == "production" ? "ERROR" : "DEBUG"
  )
}

output "multi_environment_database_url" {
  value = {
    environment  = var.environment
    database_url = local.multi_environment_database_url
    api_url      = local.api_url
    log_level    = local.log_level
  }
  sensitive = true
}

```

### Complete feature demonstration

```terraform
# Comprehensive env_variables example: Complete feature showcase
# Demonstrates filtering, regex, transformations, sensitive handling, and exclusions
#
# Before running, ensure these environment variables are set:
# export TEST_VAR1="value1"
# export TEST_VAR2="value2"
# export TEST_SENSITIVE_TOKEN="secret123"
# export TEST_EMPTY_VAR=""

# --- Test Cases ---

# Test 1: Filter by a specific list of keys
data "pyvider_env_variables" "by_keys" {
  keys = ["TEST_VAR1", "TEST_VAR2", "TEST_SENSITIVE_TOKEN", "NON_EXISTENT_VAR"]
}

# Test 2: Filter by prefix (case-sensitive)
data "pyvider_env_variables" "by_prefix_sensitive" {
  prefix = "TEST_"
}

# Test 3: Filter by prefix (case-insensitive) and transform keys to lower
data "pyvider_env_variables" "by_prefix_insensitive" {
  prefix           = "test_"
  case_sensitive   = false
  transform_keys   = "lower"
  transform_values = "upper"
}

# Test 4: Filter by regex pattern
data "pyvider_env_variables" "by_regex" {
  # Matches any keys containing 'VAR'
  regex = ".*VAR.*"
}

# Test 5: Handle sensitive keys correctly
data "pyvider_env_variables" "with_sensitive" {
  keys           = ["TEST_VAR1", "TEST_SENSITIVE_TOKEN"]
  sensitive_keys = ["TEST_SENSITIVE_TOKEN"]
}

# Test 6: Test exclude_empty flag
data "pyvider_env_variables" "with_empty" {
  keys          = ["TEST_VAR1", "TEST_EMPTY_VAR"]
  exclude_empty = true # This is the default, but we're being explicit
}

data "pyvider_env_variables" "without_empty" {
  keys          = ["TEST_VAR1", "TEST_EMPTY_VAR"]
  exclude_empty = false
}


# --- Outputs ---

output "comprehensive_by_keys_result" {
  description = "Result of filtering by specific keys."
  value       = data.pyvider_env_variables.by_keys.values
}

output "comprehensive_by_prefix_sensitive_result" {
  description = "Result of case-sensitive prefix filtering."
  value       = data.pyvider_env_variables.by_prefix_sensitive.values
}

output "comprehensive_by_prefix_insensitive_result" {
  description = "Result of case-insensitive prefix filtering with transformations."
  value       = data.pyvider_env_variables.by_prefix_insensitive.values
}

output "comprehensive_by_regex_result" {
  description = "Result of regex filtering."
  value       = data.pyvider_env_variables.by_regex.values
}

output "comprehensive_with_sensitive_result" {
  description = "Demonstrates sensitive key handling. The sensitive value should be redacted in CLI output."
  value       = data.pyvider_env_variables.with_sensitive.all_values
  sensitive   = true # Mark the whole output as sensitive for safety
}

output "comprehensive_with_sensitive_nonsensitive_part" {
  description = "The non-sensitive part of the sensitive test."
  value       = data.pyvider_env_variables.with_sensitive.values
}

output "comprehensive_with_sensitive_sensitive_part" {
  description = "The sensitive part of the sensitive test."
  value       = data.pyvider_env_variables.with_sensitive.sensitive_values
  sensitive   = true
}

output "comprehensive_exclude_empty_result" {
  description = "Should only contain TEST_VAR1."
  value       = data.pyvider_env_variables.with_empty.values
}

output "comprehensive_include_empty_result" {
  description = "Should contain both TEST_VAR1 and an empty TEST_EMPTY_VAR."
  value       = data.pyvider_env_variables.without_empty.values
}

output "comprehensive_full_environment_seen_by_provider" {
  description = "A complete dump of the environment as seen by the provider process."
  value       = data.pyvider_env_variables.by_keys.all_environment
  sensitive   = true
}

```

## Schema

### Optional

- `keys` (List of String)
- `prefix` (String)
- `regex` (String)
- `exclude_empty` (Boolean)
- `transform_keys` (String)
- `transform_values` (String)
- `case_sensitive` (Boolean)
- `sensitive_keys` (List of String)

### Read-Only

- `values` (Map of String)
- `sensitive_values` (Map of String)
- `all_values` (Map of String)
- `all_environment` (Map of String)


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