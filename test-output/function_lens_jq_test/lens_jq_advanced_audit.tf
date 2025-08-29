# Advanced JQ Examples with External Query Files
# This example demonstrates using complex JQ queries loaded from .jq files

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

# Example 1: Simple material tally using external JQ file
output "material_tally" {
  description = "Count of each material type in the system"
  value = provider::pyvider::lens_jq(
    {
      schematics = local.schematic_data,
      materials  = local.materials_data
    },
    local.simple_tally_query
  )
}

# Example 2: Full audit report correlating personnel psychology with material usage
output "full_system_audit" {
  description = "Master audit correlating personnel psychology with system components"
  value = provider::pyvider::lens_jq(
    {
      personnel      = local.personnel_data
      schematics     = local.schematic_data
      supply_chain   = local.supply_chain_data
      materials      = local.materials_data
      test_logs      = local.test_logs_data
      security       = local.security_data
      software       = local.software_data
      financials     = local.financials_data
    },
    local.master_audit_query
  )
}

# Example 3: Advanced V3 audit with numeric corrections
output "advanced_audit_v3" {
  description = "Enhanced audit with proper numeric handling"
  value = provider::pyvider::lens_jq(
    {
      personnel      = local.personnel_data
      schematics     = local.schematic_data
      supply_chain   = local.supply_chain_data
      materials      = local.materials_data
      test_logs      = local.test_logs_data
      security       = local.security_data
      software       = local.software_data
      financials     = local.financials_data
    },
    local.master_audit_v3_query
  )
}

# Example 4: Inline query example for comparison
output "high_neuroticism_owners" {
  description = "Find parts owned by people with high neuroticism anxiety"
  value = provider::pyvider::lens_jq(
    {
      personnel  = local.personnel_data
      schematics = local.schematic_data
    },
    <<-EOQ
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
  )
}