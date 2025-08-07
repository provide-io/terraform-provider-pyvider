---
page_title: "Resource: pyvider_timed_token"
description: |-
  Demonstrates creating a resource with encrypted private state.
---

# pyvider_timed_token (Resource)

The `pyvider_timed_token` resource is a demonstration component that showcases the framework's ability to manage sensitive data that should not be stored in the main state file.

When created, this resource generates a unique token and an expiration timestamp, storing both securely in the resource's encrypted private state. Only the non-sensitive `id` and `name` are stored in the `terraform.tfstate` file.

This pattern is essential for resources that interact with APIs and need to manage secret credentials like API keys, tokens, or passwords.

## Example Usage

```terraform
resource "pyvider_timed_token" "example" {
  # Configuration options here
}

output "example_id" {
  description = "The ID of the pyvider_timed_token resource"
  value       = pyvider_timed_token.example.id
}

```

## Argument Reference

## Arguments

- `name` (String, Required)
- `id` (String, Computed)
- `token` (String, Computed)
- `expires_at` (String, Computed)
