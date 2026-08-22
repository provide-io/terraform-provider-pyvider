---
page_title: "Data Source: pyvider_file_info"
subcategory: "File Operations"
description: |-
  Provides detailed information about files and directories
---
# pyvider_file_info (Data Source)

The `pyvider_file_info` data source allows you to inspect files and directories on the local filesystem. It provides detailed metadata including size, timestamps, permissions, and file type information without creating or managing the files.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


Use this data source to gather comprehensive information about files and directories, enabling you to make intelligent decisions in your Terraform configurations. Whether you're validating deployment prerequisites, implementing conditional logic based on file existence, or auditing filesystem state, this data source provides the metadata you need to build robust, environment-aware infrastructure code.

## Capabilities

This data source enables you to:

- **Conditional resource creation**: Check if files exist before creating resources or take different actions based on file presence
- **File system validation**: Verify expected files are present with correct properties before deployment
- **Deployment checks**: Validate configuration files exist and have appropriate sizes before proceeding
- **Backup verification**: Check file sizes and modification times to implement backup strategies
- **Permission auditing**: Inspect file and directory permissions to ensure security compliance
- **File type detection**: Determine whether a path is a file, directory, or symbolic link
- **Timestamp tracking**: Access creation, modification, and access times for temporal logic
- **Ownership inspection**: Verify files are owned by expected users and groups

## Example Usage

```terraform
data "pyvider_file_info" "target_file" {
  path = "/tmp/example_file.txt"
}

output "example_data" {
  description = "Data from pyvider_file_info"
  value       = data.pyvider_file_info.target_file
}

```

## More Examples

### Simple file existence and property checks

```terraform
# First, create a file to inspect.
resource "pyvider_file_content" "example" {
  filename = "/tmp/file_info_example.txt"
  content  = "This is a test file."
}

# Now, use the data source to get information about the file.
data "pyvider_file_info" "example" {
  path = pyvider_file_content.example.filename
}

output "basic_file_info_example" {
  value = {
    path    = data.pyvider_file_info.example.path
    exists  = data.pyvider_file_info.example.exists
    size    = data.pyvider_file_info.example.size
    is_file = data.pyvider_file_info.example.is_file
  }
}

```

### Complex validation and conditional logic patterns

```terraform
# Advanced file_info example: File validation and conditional logic
# Demonstrates checking file existence, directory detection, and metadata access

# Create a temporary file to test with
resource "local_file" "test_file" {
  content  = "This is a test file for file_info data source"
  filename = "/tmp/test_file.txt"
}

# Test file that exists - access all metadata
data "pyvider_file_info" "existing_file" {
  path       = local_file.test_file.filename
  depends_on = [local_file.test_file]
}

# Test file that doesn't exist - useful for conditional logic
data "pyvider_file_info" "nonexistent_file" {
  path = "/tmp/this_file_does_not_exist.txt"
}

# Test on a directory
data "pyvider_file_info" "directory" {
  path = "/tmp"
}

# Output for existing file - shows all available metadata
output "advanced_existing_file_info" {
  value = {
    path          = data.pyvider_file_info.existing_file.path
    exists        = data.pyvider_file_info.existing_file.exists
    size          = data.pyvider_file_info.existing_file.size
    is_dir        = data.pyvider_file_info.existing_file.is_dir
    is_file       = data.pyvider_file_info.existing_file.is_file
    modified_time = data.pyvider_file_info.existing_file.modified_time
  }
}

# Output for non-existent file - useful for validation
output "advanced_nonexistent_file_info" {
  value = {
    path   = data.pyvider_file_info.nonexistent_file.path
    exists = data.pyvider_file_info.nonexistent_file.exists
  }
}

# Output for directory - distinguish between files and directories
output "advanced_directory_info" {
  value = {
    path   = data.pyvider_file_info.directory.path
    exists = data.pyvider_file_info.directory.exists
    is_dir = data.pyvider_file_info.directory.is_dir
  }
}

# Real-world pattern: Validation and error handling
locals {
  advanced_file_validation = {
    advanced_is_valid       = data.pyvider_file_info.existing_file.exists && data.pyvider_file_info.existing_file.is_file
    advanced_is_directory   = data.pyvider_file_info.directory.is_dir
    advanced_file_is_recent = can(timeadd(data.pyvider_file_info.existing_file.modified_time, "24h"))
  }
}

output "advanced_validation_summary" {
  value = local.advanced_file_validation
}

```

## Schema

### Required

- `path` (String) - Path to inspect.

### Read-Only

- `exists` (Boolean) - Whether path exists.
- `size` (Number) - Size in bytes.
- `is_dir` (Boolean) - Is it a directory.
- `is_file` (Boolean) - Is it a regular file.
- `is_symlink` (Boolean) - Is it a symbolic link.
- `modified_time` (String) - Last modification time.
- `access_time` (String) - Last access time.
- `creation_time` (String) - Creation time.
- `permissions` (String) - File permissions.
- `owner` (String) - Owner username, or numeric UID on non-Unix systems.
- `group` (String) - Group name, or numeric GID on non-Unix systems.
- `mime_type` (String) - MIME type.


## Output Attributes

The data source provides comprehensive file information:

| Category | Attribute | Type | Description |
|----------|-----------|------|-------------|
| **Existence** | `exists` | bool | Whether the path exists on the filesystem |
| **Type** | `is_file` | bool | True if it's a regular file |
| | `is_dir` | bool | True if it's a directory |
| | `is_symlink` | bool | True if it's a symbolic link |
| **Size** | `size` | number | File size in bytes (0 for directories) |
| **Timestamps** | `modified_time` | string | Last modification time (ISO 8601 format) |
| | `access_time` | string | Last access time (ISO 8601 format) |
| | `creation_time` | string | File creation time (ISO 8601 format) |
| **Security** | `permissions` | string | File permissions in octal format (e.g., "0644") |
| | `owner` | string | File owner username |
| | `group` | string | File group name |
| **Content** | `mime_type` | string | MIME type of the file (e.g., "text/plain", "application/json") |

## Permission Format Reference

Permissions are returned in octal format with leading zero:

| Permission | Symbolic | Description |
|------------|----------|-------------|
| `0644` | rw-r--r-- | Owner: read/write, Group/Others: read |
| `0755` | rwxr-xr-x | Owner: read/write/execute, Group/Others: read/execute |
| `0600` | rw------- | Owner: read/write only |
| `0700` | rwx------ | Owner: read/write/execute only |
| `0400` | r-------- | Owner: read only |

## Timestamp Format

All timestamps are returned in ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

This standardized format allows for easy parsing, comparison, and manipulation using Terraform's built-in time functions like `timecmp()` and `timeadd()`.