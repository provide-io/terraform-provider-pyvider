# This file centralizes all local variable definitions.

locals {
  # Load all eight hyper-complex JSON data files.
  personnel_data      = jsondecode(file("${path.module}/personnel_records.json"))
  schematic_data      = jsondecode(file("${path.module}/project_apollo_schematics.json"))
  supply_chain_data   = jsondecode(file("${path.module}/supply_chain_database.json"))
  materials_data      = jsondecode(file("${path.module}/materials_properties.json"))
  test_logs_data      = jsondecode(file("${path.module}/test_and_validation_logs.json"))
  security_data       = jsondecode(file("${path.module}/security_audits.json"))
  software_data       = jsondecode(file("${path.module}/software_deployment_manifest.json"))
  financials_data     = jsondecode(file("${path.module}/financial_cost_centers.json"))

  # Load the JQ queries from their dedicated files.
  simple_tally_query = file("${path.module}/simple_tally.jq")
  full_audit_query   = file("${path.module}/master_audit.jq")
}
