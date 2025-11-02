# Common Patterns

This guide demonstrates practical patterns for using the pyvider provider in real-world Terraform configurations.

---

## Pattern 1: Environment-Specific Configuration

Manage different configurations across environments (dev, staging, production) using the pyvider provider.

### Problem

You need to deploy the same infrastructure with different settings for each environment.

### Solution

Use Terraform workspaces or variables with pyvider data sources to load environment-specific configuration.

```hcl
# variables.tf
variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

# main.tf
locals {
  env_configs = {
    dev = {
      api_url  = "https://dev-api.example.com"
      replicas = 1
    }
    staging = {
      api_url  = "https://staging-api.example.com"
      replicas = 2
    }
    production = {
      api_url  = "https://api.example.com"
      replicas = 5
    }
  }

  config = local.env_configs[var.environment]
}

# Create environment-specific config file
resource "pyvider_file_content" "app_config" {
  path = "${path.module}/config/${var.environment}.json"

  content = jsonencode({
    environment = var.environment
    api_url     = local.config.api_url
    replicas    = local.config.replicas
  })

  mode = "0644"
}

output "config_path" {
  value = pyvider_file_content.app_config.path
}
```

### Alternative: Environment Files

Load configuration from environment-specific files:

```hcl
# Read environment variables
data "pyvider_env_variables" "terraform_env" {
  keys = ["TERRAFORM_WORKSPACE", "ENV"]
}

locals {
  env = coalesce(
    data.pyvider_env_variables.terraform_env.values["ENV"],
    data.pyvider_env_variables.terraform_env.values["TERRAFORM_WORKSPACE"],
    "dev"
  )
}

# Create config based on environment
resource "pyvider_file_content" "deploy_config" {
  path    = "./deploy/${local.env}/config.yaml"
  content = "environment: ${local.env}\ndeployed_at: ${timestamp()}"
}
```

---

## Pattern 2: Template-Based File Generation

Generate configuration files from templates using provider functions.

### Problem

You need to create configuration files with dynamic content from Terraform variables.

### Solution

Use pyvider's string functions to build templates and generate files.

```hcl
variable "service_name" {
  default = "my-service"
}

variable "service_port" {
  default = 8080
}

variable "service_replicas" {
  default = 3
}

# Generate service configuration
locals {
  service_config_template = <<-EOT
    apiVersion: v1
    kind: Service
    metadata:
      name: ${var.service_name}
    spec:
      ports:
        - port: ${var.service_port}
          targetPort: ${var.service_port}
      replicas: ${var.service_replicas}
  EOT
}

resource "pyvider_file_content" "service_manifest" {
  path    = "${path.module}/manifests/${var.service_name}.yaml"
  content = local.service_config_template
  mode    = "0644"
}

# Generate README with uppercase service name
resource "pyvider_file_content" "service_readme" {
  path = "${path.module}/manifests/README.md"

  content = <<-EOT
    # ${provider::pyvider::upper(var.service_name)}

    Service configuration for ${var.service_name}

    **Port:** ${var.service_port}
    **Replicas:** ${var.service_replicas}
    **Generated:** ${timestamp()}
  EOT

  mode = "0644"
}

output "manifest_path" {
  value = pyvider_file_content.service_manifest.path
}
```

### Advanced: Multi-File Generation

Generate multiple configuration files from a list:

```hcl
variable "services" {
  type = map(object({
    port     = number
    replicas = number
  }))

  default = {
    api = {
      port     = 8080
      replicas = 3
    }
    worker = {
      port     = 9090
      replicas = 5
    }
  }
}

# Generate config file for each service
resource "pyvider_file_content" "service_configs" {
  for_each = var.services

  path = "${path.module}/configs/${each.key}.json"

  content = jsonencode({
    service  = each.key
    port     = each.value.port
    replicas = each.value.replicas
  })

  mode = "0644"
}

output "config_paths" {
  value = { for k, v in pyvider_file_content.service_configs : k => v.path }
}
```

---

## Pattern 3: HTTP API Integration

Interact with HTTP APIs and use responses in your Terraform configuration.

### Problem

You need to fetch data from an API to use in your Terraform deployment.

### Solution

Use the `pyvider_http_api` data source to make HTTP requests.

```hcl
# Fetch service discovery information
data "pyvider_http_api" "service_registry" {
  url    = "https://registry.example.com/api/services"
  method = "GET"

  headers = {
    "Accept"        = "application/json"
    "Authorization" = "Bearer ${var.api_token}"
  }
}

# Parse the response and extract service endpoints
locals {
  services = jsondecode(data.pyvider_http_api.service_registry.response_body)

  api_endpoint = lookup(
    { for s in local.services : s.name => s.endpoint },
    "api-service",
    "https://default-api.example.com"
  )
}

# Create config file with API endpoint
resource "pyvider_file_content" "api_config" {
  path = "${path.module}/api-config.json"

  content = jsonencode({
    api_endpoint = local.api_endpoint
    retrieved_at = timestamp()
  })

  mode = "0644"
}

output "api_endpoint" {
  value = local.api_endpoint
}
```

### POST Requests with Body

```hcl
# Register deployment with external system
data "pyvider_http_api" "register_deployment" {
  url    = "https://deploy-tracker.example.com/api/deployments"
  method = "POST"

  headers = {
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer ${var.api_token}"
  }

  request_body = jsonencode({
    environment   = var.environment
    service_name  = var.service_name
    deployed_by   = "terraform"
    timestamp     = timestamp()
  })
}

# Save deployment ID
resource "pyvider_file_content" "deployment_receipt" {
  path = "${path.module}/.deployment-id"

  content = jsondecode(
    data.pyvider_http_api.register_deployment.response_body
  ).deployment_id

  mode = "0600"  # Read-only for owner
}
```

---

## Pattern 4: Conditional Resource Creation

Create resources conditionally based on variables or environment.

### Problem

You need to create certain resources only in specific environments or conditions.

### Solution

Use the `count` or `for_each` meta-arguments with conditions.

```hcl
variable "create_debug_files" {
  description = "Create debug configuration files"
  type        = bool
  default     = false
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

# Create debug config only when enabled
resource "pyvider_file_content" "debug_config" {
  count = var.create_debug_files ? 1 : 0

  path = "${path.module}/debug.json"

  content = jsonencode({
    debug_mode  = true
    log_level   = "debug"
    environment = var.environment
  })

  mode = "0644"
}

# Create dev-only files
resource "pyvider_file_content" "dev_helpers" {
  count = var.environment == "dev" ? 1 : 0

  path = "${path.module}/.devtools"

  content = <<-EOT
    # Development Tools
    export DEBUG=1
    export LOG_LEVEL=debug
    export ENV=dev
  EOT

  mode = "0755"  # Executable
}

# Conditional directory creation
resource "pyvider_local_directory" "temp_dir" {
  count = var.environment != "production" ? 1 : 0

  path = "${path.module}/temp"
}

output "debug_config_created" {
  value = var.create_debug_files
}

output "dev_helpers_path" {
  value = var.environment == "dev" ? pyvider_file_content.dev_helpers[0].path : "Not created"
}
```

### Dynamic Conditional Creation

```hcl
variable "enabled_features" {
  description = "List of features to enable"
  type        = list(string)
  default     = ["api", "worker"]
}

locals {
  feature_configs = {
    api = {
      port = 8080
      path = "api-config.json"
    }
    worker = {
      port = 9090
      path = "worker-config.json"
    }
    scheduler = {
      port = 9091
      path = "scheduler-config.json"
    }
  }

  # Filter to only enabled features
  enabled_configs = {
    for feature in var.enabled_features :
    feature => local.feature_configs[feature]
    if contains(keys(local.feature_configs), feature)
  }
}

# Create config file for each enabled feature
resource "pyvider_file_content" "feature_configs" {
  for_each = local.enabled_configs

  path = "${path.module}/configs/${each.value.path}"

  content = jsonencode({
    feature = each.key
    port    = each.value.port
    enabled = true
  })

  mode = "0644"
}

output "enabled_features" {
  value = keys(local.enabled_configs)
}
```

---

## Pattern 5: Error Handling

Handle errors gracefully and provide helpful feedback.

### Problem

You need to validate inputs and handle errors before creating resources.

### Solution

Use preconditions, validation blocks, and try/catch functions.

```hcl
variable "config_file_path" {
  description = "Path to configuration file"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9/_.-]+$", var.config_file_path))
    error_message = "Config file path must be alphanumeric with /, _, ., or - characters."
  }
}

variable "port_number" {
  description = "Service port number"
  type        = number

  validation {
    condition     = var.port_number > 1024 && var.port_number < 65536
    error_message = "Port must be between 1024 and 65535."
  }
}

# Validate file content before creating
locals {
  config_content = jsonencode({
    port = var.port_number
  })

  # Validate JSON is parseable
  validated_config = can(jsondecode(local.config_content)) ? local.config_content : null
}

resource "pyvider_file_content" "validated_config" {
  # Pre-condition check
  lifecycle {
    precondition {
      condition     = local.validated_config != null
      error_message = "Configuration content is not valid JSON."
    }
  }

  path    = var.config_file_path
  content = local.validated_config
  mode    = "0644"
}

# Check if file exists before reading
data "pyvider_file_info" "existing_config" {
  path = var.config_file_path

  # Handle errors gracefully
  depends_on = [pyvider_file_content.validated_config]
}

output "config_exists" {
  value = try(data.pyvider_file_info.existing_config.exists, false)
}
```

### Graceful Fallbacks

```hcl
# Try to read environment variable with fallback
data "pyvider_env_variables" "optional_config" {
  keys = ["APP_CONFIG_URL", "APP_PORT"]
}

locals {
  # Use environment variable or default
  config_url = try(
    data.pyvider_env_variables.optional_config.values["APP_CONFIG_URL"],
    "https://default-config.example.com"
  )

  app_port = try(
    tonumber(data.pyvider_env_variables.optional_config.values["APP_PORT"]),
    8080
  )
}

# Create config with validated values
resource "pyvider_file_content" "app_config" {
  lifecycle {
    precondition {
      condition     = can(regex("^https://", local.config_url))
      error_message = "Config URL must start with https://"
    }

    precondition {
      condition     = local.app_port > 0 && local.app_port < 65536
      error_message = "Port must be between 1 and 65535"
    }
  }

  path = "${path.module}/app.json"

  content = jsonencode({
    config_url = local.config_url
    port       = local.app_port
  })

  mode = "0644"
}

output "config_summary" {
  value = {
    url  = local.config_url
    port = local.app_port
  }
}
```

---

## Combining Patterns

Real-world example combining multiple patterns:

```hcl
# variables.tf
variable "environment" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "service_name" {
  type = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*[a-z0-9]$", var.service_name))
    error_message = "Service name must be lowercase alphanumeric with hyphens."
  }
}

# main.tf
# Pattern 1: Environment-specific config
locals {
  env_config = {
    dev = {
      replicas = 1
      log_level = "debug"
      create_debug_files = true
    }
    staging = {
      replicas = 2
      log_level = "info"
      create_debug_files = true
    }
    production = {
      replicas = 5
      log_level = "warn"
      create_debug_files = false
    }
  }

  config = local.env_config[var.environment]
}

# Pattern 3: HTTP API Integration
data "pyvider_http_api" "service_discovery" {
  count = var.environment == "production" ? 1 : 0

  url    = "https://discovery.example.com/api/services/${var.service_name}"
  method = "GET"
}

# Pattern 2: Template-based generation
resource "pyvider_file_content" "service_config" {
  lifecycle {
    precondition {
      condition     = local.config.replicas > 0
      error_message = "Replicas must be greater than 0"
    }
  }

  path = "${path.module}/config/${var.environment}/${var.service_name}.yaml"

  content = yamlencode({
    service = {
      name      = var.service_name
      environment = var.environment
      replicas  = local.config.replicas
      log_level = local.config.log_level
    }
  })

  mode = "0644"
}

# Pattern 4: Conditional resource creation
resource "pyvider_file_content" "debug_config" {
  count = local.config.create_debug_files ? 1 : 0

  path = "${path.module}/config/${var.environment}/debug.json"

  content = jsonencode({
    debug_enabled = true
    log_level     = "debug"
    service       = var.service_name
  })

  mode = "0600"  # Restrictive permissions for debug file
}

# Outputs with error handling
output "config_path" {
  value = pyvider_file_content.service_config.path
}

output "debug_enabled" {
  value = local.config.create_debug_files
}

output "service_url" {
  value = var.environment == "production" ? try(
    jsondecode(data.pyvider_http_api.service_discovery[0].response_body).url,
    "https://${var.service_name}.example.com"
  ) : "http://localhost:${8080}"
}
```

---

## Best Practices

### 1. Use Validation

Always validate inputs to catch errors early:

```hcl
variable "port" {
  validation {
    condition     = var.port > 1024 && var.port < 65536
    error_message = "Port must be between 1024 and 65535"
  }
}
```

### 2. Use Preconditions

Validate state before creating resources:

```hcl
resource "pyvider_file_content" "config" {
  lifecycle {
    precondition {
      condition     = fileexists("${path.module}/template.txt")
      error_message = "Template file must exist"
    }
  }
}
```

### 3. Provide Defaults

Use try() and coalesce() for graceful fallbacks:

```hcl
locals {
  port = try(tonumber(var.custom_port), 8080)
  url  = coalesce(var.custom_url, "https://default.example.com")
}
```

### 4. Document Your Patterns

Add comments explaining complex logic:

```hcl
# Use production registry in prod, local cache otherwise
locals {
  # Production uses external service discovery
  # Non-prod environments use local configuration
  config_source = var.environment == "production" ? "api" : "local"
}
```

### 5. Test Edge Cases

Always test with:
- Empty values
- Missing environment variables
- Invalid inputs
- Network failures (for HTTP patterns)

---

## Next Steps

- **[Getting Started Tutorial](../getting-started.md)** - Learn the basics
- **[Resources Reference](../resources/)** - Full resource documentation
- **[Data Sources Reference](../data-sources/)** - Full data source documentation
- **[Functions Reference](../functions/)** - Provider function library

---

## Need Help?

- 📝 [Report issues](https://github.com/provide-io/terraform-provider-pyvider/issues)
- 💬 [Discussions](https://github.com/provide-io/terraform-provider-pyvider/discussions)
- 📚 [Provider Documentation](../index.md)
