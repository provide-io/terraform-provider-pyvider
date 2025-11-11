---
page_title: "Data Source: pyvider_file_info"
subcategory: "File Operations"
description: |-
  Provides detailed information about files and directories
---
# pyvider_file_info (Data Source)

The `pyvider_file_info` data source allows you to inspect files and directories on the local filesystem. It provides detailed metadata including size, timestamps, permissions, and file type information without creating or managing the files.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


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

## Examples

Explore these examples to see the data source in action:

- **[example.tf](examples/example.tf)** - Basic file information retrieval
- **[basic.tf](examples/basic.tf)** - Simple file existence and property checks
- **[advanced.tf](examples/advanced.tf)** - Complex validation and conditional logic patterns

## Argument Reference

## Schema

### Required

- `path` (String) - Path to inspect.

### Read-Only

- `exists` (String) - Whether path exists.
- `size` (String) - Size in bytes.
- `is_dir` (String) - Is it a directory.
- `is_file` (String) - Is it a regular file.
- `is_symlink` (String) - Is it a symbolic link.
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

## Related Components

- **pyvider_file_content** (Resource) - Create and manage file content on the filesystem
- **pyvider_local_directory** (Resource) - Create and manage directories
- **pyvider_env_variables** (Data Source) - Use environment variables to construct dynamic file paths

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
