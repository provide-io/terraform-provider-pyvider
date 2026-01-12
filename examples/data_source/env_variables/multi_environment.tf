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
    environment = var.environment
    database_url = local.multi_environment_database_url
    api_url = local.api_url
    log_level = local.log_level
  }
  sensitive = true
}
