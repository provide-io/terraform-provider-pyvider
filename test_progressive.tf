terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.5"
    }
  }
}

provider "pyvider" {}

# Test quick mode - should catch this validation error quickly
output "test_join" {
  value = provider::pyvider::join(", ", ["a", "b", "c"])
}

# Intentional syntax error to test --quick flag
output "syntax_error" {
  value = provider::pyvider::this_function_does_not_exist("test")
}