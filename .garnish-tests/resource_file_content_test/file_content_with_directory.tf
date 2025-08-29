# File content with directory dependency
resource "pyvider_local_directory" "app_dir" {
  path        = "${path.module}/app"
  permissions = "0o755"
}

resource "pyvider_file_content" "app_config" {
  filename = "${pyvider_local_directory.app_dir.path}/config.yaml"
  content  = yamlencode({
    application = {
      name        = var.app_name
      environment = var.environment
      features    = var.features
    }
  })
  
  depends_on = [pyvider_local_directory.app_dir]
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "my-app"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "features" {
  description = "Enabled features"
  type        = list(string)
  default     = ["logging", "metrics"]
}

output "config_file" {
  description = "Path to the configuration file"
  value       = pyvider_file_content.app_config.filename
}