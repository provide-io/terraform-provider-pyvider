
locals {
  # Load the complex JSON data from an external file
  complex_data = jsondecode(file("${path.module}/complex_data.json"))

  # This query reshapes the complex deployment data into a simplified summary.
  # The query is designed to always produce a list of objects with a
  # consistent schema, making it safe for `jq_cty`.
  container_summary_query = "[.spec.template.spec.containers[] | { name: .name, image: .image, port_count: (.ports | length), has_readiness_probe: (.readinessProbe != null) }]"
}

# --- Using the `pyvider_jq_cty` function ---
output "ex9_container_summary_from_function" {
  description = "Example 9: A complex summary object created directly by the jq_cty function."
  
  # Note: No `jsondecode()` is needed here because the function returns a native CTY value.
  value = provider::pyvider::pyvider_jq_cty(local.complex_data, local.container_summary_query)
}

# --- Using the `pyvider_jq_cty` data source ---
data "pyvider_jq_cty" "container_summary_from_ds" {
  json_input = file("${path.module}/complex_data.json")
  query      = local.container_summary_query
}

output "ex10_container_summary_from_ds" {
  description = "Example 10: The same complex summary created by the jq_cty data source."
  
  # The result is already a native Terraform object.
  value = data.pyvider_jq_cty.container_summary_from_ds.result
}