# Outputs from the complete showcase example

output "showcase_summary" {
  description = "Summary of the complete showcase"
  value = {
    timestamp = timestamp()
    components_demonstrated = 35
    environment = var.environment
  }
}