# This file executes the master audit query using the `pyvider_lens_jq` data source.

data "pyvider_lens_jq" "full_system_audit" {
  # Combine all data sources into a single JSON object to pass to the query.
  # This allows the query to reference each data source by its top-level key.
  json_input = jsonencode({
    personnel      = local.personnel_data
    schematics     = local.schematic_data
    supply_chain   = local.supply_chain_data
    materials      = local.materials_data
    test_logs      = local.test_logs_data
    security       = local.security_data
    software       = local.software_data
    financials     = local.financials_data
  })
  query = local.full_audit_query
}

output "psycho_structural_materials_audit_report" {
  description = "A complete audit report correlating a material's use to its owners' averaged personality facets, supplier info, test results, and more."
  value       = data.pyvider_lens_jq.full_system_audit.result
}

# Also run the simpler query with the standard `jq` function for comparison.
output "simple_material_type_tally" {
  description = "A simple tally of material types, using the standard jq function."
  value       = provider::pyvider::lens_jq(
    {
      schematics = local.schematic_data,
      materials  = local.materials_data
    },
    local.simple_tally_query
  )
}
