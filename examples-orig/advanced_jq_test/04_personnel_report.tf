# Report 3: Personnel, Ownership, and Psycho-Structural Correlation

# --- Simple Query ---
output "personnel_simple_owner_ids" {
  description = "A simple list of all unique owner IDs mentioned in the schematics."
  value       = provider::pyvider::lens_jq(local.schematic_data, "[.system.subsystems[]?.assemblies[]?.parts[]?.owner_ids[]?] | unique")
}

# --- Medium Complexity Inline Query ---
output "personnel_medium_clearance_levels" {
  description = "A map of personnel names to their security clearance level."
  value = provider::pyvider::lens_jq(
    local.personnel_data,
    "[.records[]? | {(.name): .clearance_level}] | add"
  )
}

# --- Hyper Complex Query from File ---
data "pyvider_lens_jq" "personnel_complex_audit" {
  json_input = jsonencode(local.full_system_data)
  query      = local.full_audit_query
}

output "personnel_hyper_complex_audit_report" {
  description = "The full audit report, focused on personnel."
  value       = data.pyvider_lens_jq.personnel_complex_audit.result
}
