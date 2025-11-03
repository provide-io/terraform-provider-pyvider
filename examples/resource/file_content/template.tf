# Config file generation with templates

locals {
  template_app_config = {
    name = "my-application"
    version = "1.0.0"
    port = 8080
    database = {
      host = "localhost"
      port = 5432
      name = "myapp"
    }
    features = ["api", "web", "admin"]
  }

  # Build nginx config
  nginx_config = provider::pyvider::join("\n", [
    "server {",
    "  listen ${local.template_app_config.port};",
    "  server_name ${local.template_app_config.name};",
    "",
    "  location / {",
    "    proxy_pass http://localhost:3000;",
    "  }",
    "}"
  ])

  # Build env file
  env_file = provider::pyvider::join("\n", [
    "APP_NAME=${local.template_app_config.name}",
    "APP_VERSION=${local.template_app_config.version}",
    "APP_PORT=${local.template_app_config.port}",
    "DB_HOST=${local.template_app_config.database.host}",
    "DB_PORT=${local.template_app_config.database.port}",
    "DB_NAME=${local.template_app_config.database.name}"
  ])
}

resource "pyvider_file_content" "nginx_config" {
  filename = "/tmp/${local.template_app_config.name}-nginx.conf"
  content  = local.nginx_config
}

resource "pyvider_file_content" "env_file" {
  filename = "/tmp/${local.template_app_config.name}.env"
  content  = local.env_file
}

output "template_app_config" {
  value = {
    nginx = pyvider_file_content.nginx_config.filename
    env   = pyvider_file_content.env_file.filename
  }
}
