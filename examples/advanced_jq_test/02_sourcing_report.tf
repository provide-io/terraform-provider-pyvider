# Report 1: Sourcing and Materials
output "sourcing_simple_supplier_list" {
  description = "A simple list of all supplier names."
  value       = provider::pyvider::lens_jq(local.supply_chain_data, "[.suppliers[]?.name]")
}
output "sourcing_medium_as9100_suppliers" {
  description = "A list of suppliers that are AS9100 certified."
  value = provider::pyvider::lens_jq(
    local.supply_chain_data,
    "[.suppliers[]? | select(.certifications? | index(\"AS9100\")) | .name]"
  )
}
# This query is wrapped in `[` and `]` to guarantee it produces a single array output.
data "pyvider_lens_jq" "sourcing_hyper_complex_material_audit" {
  json_input = jsonencode(local.full_system_data)
  query      = "[ .schematics.system.subsystems[]?.assemblies[]?.parts[]? as $part | { part_name: $part.name, supplier: (.supply_chain.suppliers[]? | select(.id == $part.supplier_id) | .name // \"In-House\"), materials: [ $part.material_ids[]? as $mid | .materials.materials[]? | select(.material_id == $mid) | .element ] } ]"
}
output "sourcing_hyper_complex_material_audit_report" {
  description = "A detailed audit of materials and their suppliers for each part."
  value       = data.pyvider_lens_jq.sourcing_hyper_complex_material_audit.result
}
