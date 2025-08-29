# Advanced JQ Data Source Examples with External Query Files
# This example demonstrates using the lens_jq data source with complex queries from .jq files

# Load all the data files from fixtures
locals {
  # Personnel data with personality profiles
  personnel_data = jsondecode(file("../fixtures/personnel_records.json"))
  
  # System schematics with parts and assemblies
  schematic_data = jsondecode(file("../fixtures/project_apollo_schematics.json"))
  
  # Supply chain information
  supply_chain_data = jsondecode(file("../fixtures/supply_chain_database.json"))
  
  # Materials properties database
  materials_data = jsondecode(file("../fixtures/materials_properties.json"))
  
  # Test and validation logs
  test_logs_data = jsondecode(file("../fixtures/test_and_validation_logs.json"))
  
  # Security audit data
  security_data = jsondecode(file("../fixtures/security_audits.json"))
  
  # Software deployment manifest
  software_data = jsondecode(file("../fixtures/software_deployment_manifest.json"))
  
  # Financial cost centers
  financials_data = jsondecode(file("../fixtures/financial_cost_centers.json"))
  
  # Load JQ queries from files
  simple_tally_query = file("../fixtures/simple_tally.jq")
  master_audit_query = file("../fixtures/master_audit.jq")
  master_audit_v3_query = file("../fixtures/master_audit_v3.jq")
}

# Data source for simple material tally
data "pyvider_lens_jq" "material_tally" {
  json_input = jsonencode({
    schematics = local.schematic_data,
    materials  = local.materials_data
  })
  query = local.simple_tally_query
}

# Data source for full audit report
data "pyvider_lens_jq" "full_system_audit" {
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
  query = local.master_audit_query
}

# Data source for V3 audit with numeric handling
data "pyvider_lens_jq" "advanced_audit_v3" {
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
  query = local.master_audit_v3_query
}

# Data source with inline query for finding high anxiety owners
data "pyvider_lens_jq" "high_anxiety_parts" {
  json_input = jsonencode({
    personnel  = local.personnel_data
    schematics = local.schematic_data
  })
  query = <<-EOQ
    [
      .schematics.system.subsystems[]?.assemblies[]?.parts[]? as $part |
      $part.owner_ids[]? as $owner_id |
      .personnel.records[]? | select(.person_id == $owner_id) |
      select(.personality_profile.neuroticism.facets.anxiety > 7) |
      {
        part_name: $part.name,
        owner_name: .name,
        anxiety_level: .personality_profile.neuroticism.facets.anxiety
      }
    ]
  EOQ
}

# Outputs to display the results
output "material_tally_result" {
  description = "Count of each material type in the system"
  value       = data.pyvider_lens_jq.material_tally.result
}

output "full_audit_report" {
  description = "Master audit correlating personnel psychology with system components"
  value       = data.pyvider_lens_jq.full_system_audit.result
}

output "advanced_audit_v3_report" {
  description = "Enhanced audit with proper numeric handling"
  value       = data.pyvider_lens_jq.advanced_audit_v3.result
}

output "high_anxiety_parts_list" {
  description = "Parts owned by people with high neuroticism anxiety"
  value       = data.pyvider_lens_jq.high_anxiety_parts.result
}