# Use the lens_jq data source to extract a field from a JSON object.
data "pyvider_lens_jq" "user_extract" {
  json_input = jsonencode({
    user = {
      name  = "John Doe"
      email = "john@example.com"
    }
  })
  query = ".user.name"
}

output "basic_extracted_name" {
  description = "The name extracted from the JSON input."
  value       = data.pyvider_lens_jq.user_extract.result
}
