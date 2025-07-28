locals {
  personnel_data      = jsondecode(file("${path.module}/personnel_records.json"))
  schematic_data      = jsondecode(file("${path.module}/project_apollo_schematics.json"))
  supply_chain_data   = jsondecode(file("${path.module}/supply_chain_database.json"))
  materials_data      = jsondecode(file("${path.module}/materials_properties.json"))
  test_logs_data      = jsondecode(file("${path.module}/test_and_validation_logs.json"))
  security_data       = jsondecode(file("${path.module}/security_audits.json"))
  software_data       = jsondecode(file("${path.module}/software_deployment_manifest.json"))
  financials_data     = jsondecode(file("${path.module}/financial_cost_centers.json"))

  full_system_data = {
    personnel   = local.personnel_data, schematics = local.schematic_data,
    supply_chain= local.supply_chain_data, materials  = local.materials_data,
    test_logs   = local.test_logs_data, security   = local.security_data,
    software    = local.software_data, financials = local.financials_data
  }
  full_audit_query = file("${path.module}/master_audit_v3.jq")
}
