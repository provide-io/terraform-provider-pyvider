
locals {
  # Load the complex JSON data from an external file
  complex_data = jsondecode(file("${path.module}/complex_data.json"))

  # This query reshapes the complex deployment data into a simplified summary.
  # The query is designed to always produce a list of objects with a
  # consistent schema, making it safe for `lens_jq`.
  container_summary_query = "[.spec.template.spec.containers[] | { name: .name, image: .image, port_count: (.ports | length), has_readiness_probe: (.readinessProbe != null) }]"
}

# --- Using the `pyvider_lens_jq` function ---
output "ex9_container_summary_from_function" {
  description = "Example 9: A complex summary object created directly by the lens_jq function."

  value = provider::pyvider::lens_jq(local.complex_data, local.container_summary_query)
}

# --- Using the `pyvider_lens_jq` data source ---
data "pyvider_lens_jq" "container_summary_from_ds" {
  json_input = file("${path.module}/complex_data.json")
  query      = local.container_summary_query
}

output "ex10_container_summary_from_ds" {
  description = "Example 10: The same complex summary created by the lens_jq data source."

  value = data.pyvider_lens_jq.container_summary_from_ds.result
}
