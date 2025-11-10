---
page_title: "Resource: pyvider_local_directory"
subcategory: "File Operations"
description: |-
  Manages directories on the local filesystem with permissions and metadata tracking
---
# pyvider_local_directory (Resource)

The `pyvider_local_directory` resource allows you to create, manage, and monitor directories on the local filesystem. It automatically tracks directory metadata including file counts and provides fine-grained permission control.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


This resource enables declarative directory management as part of your infrastructure-as-code workflow. Whether you're setting up project structures, managing application workspaces, or ensuring proper filesystem permissions, this resource provides the tools to create and maintain directories with consistent permissions and automatic state tracking.

## Capabilities

This resource enables you to:

- **Project structure**: Create consistent directory layouts for applications and deployments
- **Permission management**: Ensure directories have correct access permissions using octal notation
- **Workspace initialization**: Set up development or deployment environments programmatically
- **Directory monitoring**: Track changes in directory contents with automatic file counting
- **Lifecycle management**: Full CRUD operations for directories
- **Import existing directories**: Bring existing directories under Terraform management
- **Dependency coordination**: Ensure directories are created in the proper order
- **Metadata tracking**: Monitor the number of files and subdirectories

## Example Usage

```terraform
resource "pyvider_local_directory" "example" {
  path = "/tmp/pyvider_example_directory"
}

output "example_id" {
  description = "The ID of the pyvider_local_directory resource"
  value       = pyvider_local_directory.example.id
}

```

## Examples

Explore these examples to see the resource in action:

- **[example.tf](examples/example.tf)** - Basic directory creation
- **[basic.tf](examples/basic.tf)** - Simple directory management
- **[permissions.tf](examples/permissions.tf)** - Permission control and management
- **[project_structure.tf](examples/project_structure.tf)** - Creating complex directory structures

## Argument Reference



## Computed Attributes

The resource provides the following computed attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | string | The absolute path of the directory |
| `file_count` | number | Number of direct children (files and subdirectories) in the directory |

## Permission Format Reference

The `permissions` attribute uses octal notation with the `0o` prefix:

| Permission | Octal | Symbolic | Description |
|------------|-------|----------|-------------|
| `0o755`    | 755   | rwxr-xr-x | Owner: full access, Group/Others: read and execute |
| `0o750`    | 750   | rwxr-x--- | Owner: full access, Group: read and execute, Others: none |
| `0o700`    | 700   | rwx------ | Owner: full access only |
| `0o775`    | 775   | rwxrwxr-x | Owner/Group: full access, Others: read and execute |
| `0o770`    | 770   | rwxrwx--- | Owner/Group: full access, Others: none |

## Import

Directories can be imported into Terraform state using either the CLI or configuration-based import.

### CLI Import

```bash
terraform import pyvider_local_directory.example /path/to/existing/directory
```

### Configuration Import (Terraform 1.5+)

```terraform
import {
  to = pyvider_local_directory.example
  id = "/path/to/existing/directory"
}

resource "pyvider_local_directory" "example" {
  path = "/path/to/existing/directory"
  # permissions will be read during import
}
```

### Import Process

During import, the resource will:
1. Verify the directory exists and is accessible
2. Read the current directory permissions
3. Count the number of files and subdirectories
4. Store the directory state in Terraform state

Note: If you specify `permissions` in your configuration, ensure they match the existing directory permissions to avoid drift detection on the next apply.

## File Count Monitoring

The `file_count` attribute provides the number of direct children in the directory:

```terraform
resource "pyvider_local_directory" "monitored" {
  path = "/tmp/monitored"
}

# Use file count in conditional logic or outputs
output "directory_contents" {
  value = "Directory has ${pyvider_local_directory.monitored.file_count} items"
}
```

## Related Components

- **pyvider_file_content** (Resource) - Create files within managed directories
- **pyvider_file_info** (Data Source) - Check directory existence without managing it
- **pyvider_env_variables** (Data Source) - Use environment variables in directory paths