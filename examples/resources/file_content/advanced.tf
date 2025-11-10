# Create a JSON configuration file using a template and local variables.
variable "environment" {
  type    = string
  default = "development"
}

locals {
  advanced_db_host = var.environment == "production" ? "prod.db.example.com" : "dev.db.example.com"
}

resource "pyvider_file_content" "json_config" {
  filename = "/tmp/app_config.json"
  content = jsonencode({
    app_name = "my-terraform-app"
    version  = "1.0.0"
    debug    = var.environment != "production"
    database = {
      host = local.advanced_db_host
      port = 5432
    }
  })
}

output "advanced_config_hash" {
  description = "Hash of the generated JSON configuration file."
  value       = pyvider_file_content.json_config.content_hash
}
