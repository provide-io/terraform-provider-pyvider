locals {
  example_result = lens_jq(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of lens_jq function"  
  value       = local.example_result
}
