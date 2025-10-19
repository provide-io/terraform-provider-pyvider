# Report 2: Engineering and Test Results
output "engineering_simple_subsystem_names" {
  value = provider::pyvider::lens_jq(local.schematic_data, "[.system.subsystems[]?.name]")
}
output "engineering_medium_failed_parts" {
  value = provider::pyvider::lens_jq(local.test_logs_data, "[.results[]? | select(.passed == false) | .part_id]")
}
data "pyvider_lens_jq" "engineering_complex_audit" {
  json_input = jsonencode(local.full_system_data)
  query      = "[.schematics.system.subsystems[]?.assemblies[]?.parts[]? as $part | { part_id: $part.id, name: $part.name, criticality: ($part.criticality // \"unknown\"), test_passed: (.test_logs.results[]? | select(.part_id == $part.id) | .passed // false), owner_ids: ($part.owner_ids? // []) }]"
}
output "engineering_hyper_complex_audit_report" {
  value = data.pyvider_lens_jq.engineering_complex_audit.result
}
