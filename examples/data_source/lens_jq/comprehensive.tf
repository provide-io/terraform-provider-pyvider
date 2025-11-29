# Comprehensive lens_jq example: Complex jq queries and data transformations
# Demonstrates the full range of jq capabilities: filtering, projecting, transforming

locals {
  # Sample data for demonstrating the jq function.
  # The function can accept raw Terraform objects directly.
  comprehensive_sample_data_for_func = {
    comprehensive_items = [
      { "name" : "Laptop", "stock" : 15, "tags" : ["electronics", "sale"], "price" : 999 },
      { "name" : "Mouse", "stock" : 150, "tags" : ["electronics", "accessory"], "price" : 25 },
      { "name" : "Keyboard", "stock" : 75, "tags" : ["electronics", "accessory"], "price" : 75 },
      { "name" : "Monitor", "stock" : 25, "tags" : ["electronics"], "price" : 350 }
    ],
    "store_location" : "Warehouse A",
    "last_updated" : "2025-06-25T10:00:00Z"
  }

  # Sample data for demonstrating the jq data source.
  # The data source requires a valid JSON string as input.
  sample_json_string_for_ds = jsonencode({
    users = [
      { "name" : "Alice", "id" : "a1", "roles" : ["admin", "editor"], "active" : true },
      { "name" : "Bob", "id" : "b2", "roles" : ["viewer"], "active" : true },
      { "name" : "Charlie", "id" : "c3", "roles" : ["editor"], "active" : false }
    ],
    "metadata" = { "timestamp" : "2025-06-25T12:00:00Z", "source" : "test-data" }
  })
}

# ===================================================================
# Example 1: Simple Field Extraction (Result is a primitive)
# ===================================================================
output "comprehensive_field_extraction" {
  description = "Example 1: Extracts the 'store_location' field."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, ".store_location")
}

# ===================================================================
# Example 2: Array Indexing (Result is a primitive)
# ===================================================================
output "comprehensive_array_indexing" {
  description = "Example 2: Extracts the name of the first item in the 'items' array."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, ".comprehensive_items[0].name")
}

# ===================================================================
# Example 3: Array Projection (Result is a list)
# ===================================================================
output "comprehensive_array_projection" {
  description = "Example 3: Creates a new array containing only the names of all items."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, "[.comprehensive_items[].name]")
}

# ===================================================================
# Example 4: Filtering an Array (Result is a list of objects)
# ===================================================================
output "comprehensive_array_filtering" {
  description = "Example 4: Filters for items tagged as 'accessory'."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, "[.comprehensive_items[] | select(.tags[] == \"accessory\")]")
}

# ===================================================================
# Example 5: Filtering and Projecting (Result is a list)
# ===================================================================
output "comprehensive_filter_and_project" {
  description = "Example 5: Filters for 'accessory' items and returns only their names."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, "[.comprehensive_items[] | select(.tags[] == \"accessory\") | .name]")
}

# ===================================================================
# Example 6: Creating a New Object (Result is an object)
# ===================================================================
output "comprehensive_create_object" {
  description = "Example 6: Creates a custom stock report object."
  value = provider::pyvider::lens_jq(
    local.comprehensive_sample_data_for_func,
    "{ report_date: .last_updated, inventory: [ .comprehensive_items[] | { item: .name, quantity: .stock, is_electronic: (.tags[] | contains(\"electronics\")) } ] }"
  )
}

# ===================================================================
# Example 7: Complex Filtering (Result is a list of objects)
# ===================================================================
output "comprehensive_complex_filter" {
  description = "Example 7: Finds items on sale with stock less than 20."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, "[.comprehensive_items[] | select((.tags[] == \"sale\") and .stock < 20)]")
}

# ===================================================================
# Example 8: Using the lens_jq Data Source
# ===================================================================
data "pyvider_lens_jq" "get_active_admins" {
  json_input = local.sample_json_string_for_ds
  query      = ".users[] | select(.active == true and (.roles[] | contains(\"admin\"))) | .name"
}

output "comprehensive_data_source_result" {
  description = "Example 8: Result from the lens_jq data source."
  # The data source returns a string. Since the query result is a primitive ("Alice"),
  # we do not need jsondecode() here. If the query returned a list or object, we would.
  value = data.pyvider_lens_jq.get_active_admins.result
}

# ===================================================================
# Real-world pattern: Dynamic configuration filtering
# ===================================================================
data "pyvider_lens_jq" "filter_active_users" {
  json_input = local.sample_json_string_for_ds
  query      = "[.users[] | select(.active == true)] | length"
}

output "comprehensive_active_users_count" {
  description = "Count of active users using jq aggregation"
  value       = data.pyvider_lens_jq.filter_active_users.result
}
