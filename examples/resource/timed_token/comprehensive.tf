# Basic timed token examples

# Example 1: Simple token generation
resource "pyvider_timed_token" "simple" {
  name = "basic-example-token"
}

# Example 2: Token for API integration
resource "pyvider_timed_token" "api_auth" {
  name = "api-integration-token"
}

# Create configuration file with token metadata
resource "pyvider_file_content" "api_config" {
  filename = "/tmp/api_config.json"
  content = jsonencode({
    authentication = {
      token_id   = pyvider_timed_token.api_auth.id
      token_name = pyvider_timed_token.api_auth.name
      expires_at = pyvider_timed_token.api_auth.expires_at
      # Note: actual token value is sensitive and not exposed in config
    }
    api_endpoint    = "https://api.example.com/v1"
    timeout_seconds = 30
  })
}

# Example 3: Multiple tokens for different services
resource "pyvider_timed_token" "database" {
  name = "database-service-token"
}

resource "pyvider_timed_token" "cache" {
  name = "cache-service-token"
}

# Summary file
resource "pyvider_file_content" "token_summary" {
  filename = "/tmp/token_summary.txt"
  content = join("\n", [
    "=== Token Summary ===",
    "",
    "Simple Token:",
    "  ID: ${pyvider_timed_token.simple.id}",
    "  Name: ${pyvider_timed_token.simple.name}",
    "  Expires: ${pyvider_timed_token.simple.expires_at}",
    "",
    "API Token:",
    "  ID: ${pyvider_timed_token.api_auth.id}",
    "  Expires: ${pyvider_timed_token.api_auth.expires_at}",
    "",
    "Service Tokens:",
    "  Database: ${pyvider_timed_token.database.id}",
    "  Cache: ${pyvider_timed_token.cache.id}",
  ])
}

output "comprehensive_basic_token_examples" {
  description = "Information about created tokens (sensitive values excluded)"
  sensitive   = true
  value = {
    simple_token = {
      id         = pyvider_timed_token.simple.id
      name       = pyvider_timed_token.simple.name
      expires_at = pyvider_timed_token.simple.expires_at
    }
    api_token = {
      id         = pyvider_timed_token.api_auth.id
      name       = pyvider_timed_token.api_auth.name
      expires_at = pyvider_timed_token.api_auth.expires_at
    }
    service_tokens = {
      database = pyvider_timed_token.database.name
      cache    = pyvider_timed_token.cache.name
    }
  }
}
