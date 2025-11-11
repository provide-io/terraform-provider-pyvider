---
page_title: "Resource: pyvider_private_state_verifier"
subcategory: "Test Mode"
description: |-
  Verifies private state encryption and decryption functionality in Terraform resources
---
# pyvider_private_state_verifier (Resource)

The `pyvider_private_state_verifier` resource is designed for testing and verifying the private state encryption functionality of Terraform providers. It demonstrates how sensitive data can be securely stored in private state, encrypted by Terraform, and properly decrypted when needed.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


This resource showcases Terraform's private state encryption capabilities by implementing a complete encryption/decryption verification workflow. It takes an input value, generates a secret token, stores it in encrypted private state, and then retrieves and decrypts it to validate the entire process. This makes it an invaluable tool for provider developers, security audits, and educational demonstrations of Terraform's built-in encryption mechanisms.

## Capabilities

This resource enables you to:

- **Provider development**: Test private state encryption mechanisms during Terraform provider development
- **Security validation**: Verify that sensitive data is properly encrypted in Terraform state files
- **Testing workflows**: Validate encryption and decryption cycles in automated test suites
- **Compliance verification**: Ensure private state handling meets organizational security requirements
- **Educational purposes**: Learn and demonstrate how Terraform private state encryption works
- **Integration testing**: Verify private state works correctly with other Terraform resources
- **Encryption lifecycle**: Demonstrate the complete create, store, retrieve, and decrypt workflow

## Example Usage

```terraform
resource "pyvider_private_state_verifier" "example" {
  input_value = "test-value"
}

output "example_verification" {
  description = "The verification result of the pyvider_private_state_verifier resource"
  value = {
    input           = pyvider_private_state_verifier.example.input_value
    decrypted_token = pyvider_private_state_verifier.example.decrypted_token
  }
  sensitive = true
}

```

## Examples

Explore these examples to see the resource in action:

- **[example.tf](examples/example.tf)** - Basic private state verification
- **[basic.tf](examples/basic.tf)** - Simple encryption testing
- **[comprehensive.tf](examples/comprehensive.tf)** - Advanced verification patterns
- **[provider_alias.tf](examples/provider_alias.tf)** - Multi-provider testing scenarios

## Argument Reference

## Schema

### Required

- `input_value` (String) - 

### Read-Only

- `decrypted_token` (String) - 


## Computed Attributes

The resource provides the following computed attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `decrypted_token` | string | The decrypted secret token retrieved from private state |

## How Private State Verification Works

The resource demonstrates the complete lifecycle of private state encryption:

### 1. Creation Phase
- Takes an `input_value` as configuration
- Generates a secret token using the formula: `SECRET_FOR_{INPUT_VALUE_UPPER}`
- Stores the secret token in encrypted private state
- Returns a planned state with the decrypted token marked as computed

### 2. Apply Phase
- Retrieves the encrypted private state from Terraform
- Terraform automatically decrypts the private state
- Populates the `decrypted_token` attribute with the decrypted value
- Validates that the decryption process completed successfully

### 3. Read Phase
- Returns the current state including the decrypted token
- Demonstrates that private state persists across Terraform operations
- Shows that encrypted data remains accessible when needed

### 4. Verification
- Compares input and output to ensure the encryption/decryption cycle worked correctly
- Validates that sensitive data was never stored in plain text in the state file
- Confirms that Terraform's encryption mechanisms are functioning as expected

## Security Features Demonstrated

### Private State Encryption

```terraform
resource "pyvider_private_state_verifier" "encryption_test" {
  input_value = "sensitive-data"
}

# The secret token is encrypted in private state
# Only the decrypted result is available as an attribute
output "encryption_works" {
  value = pyvider_private_state_verifier.encryption_test.decrypted_token
  # Will output: "SECRET_FOR_SENSITIVE-DATA"
}
```

### State File Security Model

| Data Element | Storage Location | Visibility |
|--------------|------------------|------------|
| Input data | Regular state | Visible in state file |
| Secret generation | During resource creation | Not stored directly |
| Secret storage | Private state (encrypted) | Not visible in state file |
| Decrypted output | Computed attribute | Available after decryption |

### Verification Pattern

```terraform
locals {
  test_input = "my-test-value"
  expected_secret = "SECRET_FOR_${upper(local.test_input)}"
}

resource "pyvider_private_state_verifier" "verify" {
  input_value = local.test_input
}

# Verify the encryption/decryption cycle worked
output "verification_passed" {
  value = pyvider_private_state_verifier.verify.decrypted_token == local.expected_secret
}
```

## Testing Multiple Scenarios

```terraform
# Test different input types
resource "pyvider_private_state_verifier" "alphanumeric" {
  input_value = "test123"
}

resource "pyvider_private_state_verifier" "special_chars" {
  input_value = "test-with-dashes"
}

# Verify all tests pass
locals {
  all_tests_pass = (
    pyvider_private_state_verifier.alphanumeric.decrypted_token == "SECRET_FOR_TEST123" &&
    pyvider_private_state_verifier.special_chars.decrypted_token == "SECRET_FOR_TEST-WITH-DASHES"
  )
}
```

## Integration with Other Resources

```terraform
# Combine with other resources for comprehensive testing
resource "pyvider_timed_token" "test_token" {
  name = "verification-test-token"
}

resource "pyvider_private_state_verifier" "integrated_test" {
  input_value = "integration-with-${pyvider_timed_token.test_token.id}"
}

# Verify integration works correctly
locals {
  integration_test_passed = (
    pyvider_timed_token.test_token.id != null &&
    pyvider_private_state_verifier.integrated_test.decrypted_token != null
  )
}
```

## Import

```bash
terraform import pyvider_private_state_verifier.example <id>
```

## Related Components

- **pyvider_timed_token** (Resource) - Time-based token generation for testing
- **pyvider_simple_resource** (Resource) - Basic resource for comparison testing
- **pyvider_provider_config** (Resource) - Provider configuration management

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
