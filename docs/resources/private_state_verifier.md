---
page_title: "Resource: pyvider_private_state_verifier"
description: |-
  A diagnostic resource to verify the private state encryption lifecycle.
---

# pyvider_private_state_verifier (Resource)

This is a diagnostic resource intended for testing and demonstrating the `pyvider` framework's private state management capabilities.

During the `plan` phase, it generates a secret token based on its input and stores it in the resource's encrypted private state. During the `apply` phase, it decrypts this token and exposes it as a computed attribute, `decrypted_token`.

A successful `apply` of this resource confirms that the provider's encryption key is correctly configured and the plan/apply lifecycle for sensitive data is functioning as expected.

## Example Usage

```terraform
resource "pyvider_private_state_verifier" "example" {
  # Configuration options here
}

output "example_id" {
  description = "The ID of the pyvider_private_state_verifier resource"
  value       = pyvider_private_state_verifier.example.id
}

```

## Argument Reference

