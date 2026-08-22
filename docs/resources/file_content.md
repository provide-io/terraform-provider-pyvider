---
page_title: "Resource: pyvider_file_content"
subcategory: "File Operations"
description: |-
  Manages the content of a file on the local filesystem
---
# pyvider_file_content (Resource)

The `pyvider_file_content` resource allows you to create, read, update, and delete files on the local filesystem. It automatically tracks content changes using SHA256 hashing and provides atomic write operations to ensure file integrity.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


This resource enables declarative file management within your Terraform configurations, allowing you to create configuration files, render templates, and maintain files as part of your infrastructure-as-code workflow. With automatic content tracking and atomic writes, you can confidently manage files knowing that changes are properly detected and updates are performed safely.

## Capabilities

This resource enables you to:

- **Configuration files**: Create and manage application configuration files as code
- **Template rendering**: Generate files from dynamic content using Terraform expressions
- **Atomic file operations**: Ensure file writes are safe and complete, preventing partial writes
- **Content tracking**: Monitor file changes with automatic SHA256 hash calculation
- **Lifecycle management**: Full CRUD (Create, Read, Update, Delete) operations for files
- **Import existing files**: Bring existing files under Terraform management
- **Content validation**: Track when file content changes and trigger updates
- **Dependency management**: Coordinate file creation with other resources using depends_on

## Example Usage

```terraform
resource "pyvider_file_content" "example" {
  filename = "/tmp/pyvider_example.txt"
  content  = "This is an example file created by Terraform."
}

output "example_file" {
  description = "The filename and hash of the created file"
  value = {
    filename     = pyvider_file_content.example.filename
    content_hash = pyvider_file_content.example.content_hash
    exists       = pyvider_file_content.example.exists
  }
}

```

## More Examples

### Simple configuration file management

```terraform
# Create a simple file with specified content.
resource "pyvider_file_content" "readme" {
  filename = "/tmp/pyvider_readme.txt"
  content  = "This file was created by Terraform."
}

output "basic_readme_details" {
  description = "Details about the created file."
  value = {
    filename     = pyvider_file_content.readme.filename
    exists       = pyvider_file_content.readme.exists
    content_hash = pyvider_file_content.readme.content_hash
  }
}

```

### Complex content generation patterns

```terraform
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

```

### Dynamic template rendering

```terraform
# Config file generation with templates

locals {
  template_app_config = {
    name    = "my-application"
    version = "1.0.0"
    port    = 8080
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

```

### Lifecycle management and dependencies

```terraform
# Lifecycle example: Create, update, and verification patterns
# Demonstrates the full CRUD lifecycle of file_content resources

# Create file
resource "pyvider_file_content" "test_create" {
  filename = "/tmp/pyvider_test_create.txt"
  content  = "This is a test file created by Pyvider"
}

# Update file (in a separate apply)
resource "pyvider_file_content" "test_update" {
  filename = "/tmp/pyvider_test_update.txt"
  content  = "Initial content"
}

# Read the file using local_file to verify
data "local_file" "verify_create" {
  filename   = pyvider_file_content.test_create.filename
  depends_on = [pyvider_file_content.test_create]
}

output "lifecycle_created_file" {
  value = {
    filename     = pyvider_file_content.test_create.filename
    content      = pyvider_file_content.test_create.content
    exists       = pyvider_file_content.test_create.exists
    content_hash = pyvider_file_content.test_create.content_hash
  }
}

output "lifecycle_verification" {
  value = {
    file_content = data.local_file.verify_create.content
    matches      = data.local_file.verify_create.content == pyvider_file_content.test_create.content
  }
}

# Run apply, then modify the content and run apply again to test updates
output "lifecycle_update_instructions" {
  value = "To test update: Change 'test_update' resource content to 'Updated content' and apply again"
}

```

## Schema

### Required

- `filename` (String)
- `content` (String)

### Read-Only

- `exists` (Boolean)
- `content_hash` (String)


## Computed Attributes

The resource provides the following computed attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `exists` | bool | Whether the file currently exists on the filesystem |
| `content_hash` | string | SHA256 hash of the file content for change detection |

## Import

Files can be imported into Terraform state using either the CLI or configuration-based import.

### CLI Import

```bash
terraform import pyvider_file_content.example /path/to/existing/file.txt
```

### Configuration Import (Terraform 1.5+)

```terraform
import {
  to = pyvider_file_content.example
  id = "/path/to/existing/file.txt"
}

resource "pyvider_file_content" "example" {
  filename = "/path/to/existing/file.txt"
  content  = "existing content will be read during import"
}
```

### Import Process

During import, the resource will:
1. Read the current file content from the specified path
2. Calculate the SHA256 hash of the content
3. Set the `exists` attribute to `true`
4. Store the content and hash in Terraform state

Note: The `content` attribute in your configuration should match the existing file content to avoid drift detection on the next apply.