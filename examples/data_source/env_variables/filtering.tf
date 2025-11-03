# Environment variable filtering examples

# Filter by prefix with case-sensitive matching
data "pyvider_env_variables" "app_config" {
  prefix = "APP_"
}

# Complex regex patterns
data "pyvider_env_variables" "url_vars" {
  regex = ".*_URL$"  # Matches any variable ending in _URL
}

data "pyvider_env_variables" "credential_vars" {
  regex = ".*(KEY|SECRET|TOKEN|PASSWORD).*"  # Security-related variables
}

# Categorize variables by type
locals {
  filtering_variable_categories = {
    filtering_urls = {
      for k, v in data.pyvider_env_variables.url_vars.values : k => v
    }
    credentials = {
      for k, v in data.pyvider_env_variables.credential_vars.values : k => {
        length = length(v)
        has_value = v != ""
      }
    }
  }
}

output "filtering_urls" {
  description = "Results of various filtering approaches"
  value = {
    app_config_count = length(data.pyvider_env_variables.app_config.values)
    url_matches = length(data.pyvider_env_variables.url_vars.values)
    credential_matches = length(data.pyvider_env_variables.credential_vars.values)
  }
}
