---
page_title: "Resource: pyvider_timed_token"
description: |-
  Terraform resource for pyvider_timed_token
---
# pyvider_timed_token (Resource)

Terraform resource for pyvider_timed_token

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
resource "pyvider_timed_token" "simple_token" {
  name = "test-token"
}

output "example_token_id" {
  description = "The ID of the pyvider_timed_token resource"
  value       = pyvider_timed_token.simple_token.id
  sensitive   = true
}

```

## Argument Reference



## Import

```bash
terraform import pyvider_timed_token.example <id>
```