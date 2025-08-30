locals {
  example_result = lookup(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of lookup function"  
  value       = local.example_result
}
