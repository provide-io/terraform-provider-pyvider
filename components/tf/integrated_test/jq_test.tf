# pyvider/components/tf/jq_test/main.tf

locals {
  # Sample data for demonstrating the jq function.
  # The function can accept raw Terraform objects directly.
  sample_data_for_func = {
    items = [
      { "name" : "Laptop", "stock" : 15, "tags" : ["electronics", "sale"], "specs" : { "cpu" : "i7", "ram_gb" : 16 } },
      { "name" : "Mouse", "stock" : 150, "tags" : ["electronics", "accessory"], "specs" : { "dpi" : 1200 } },
      { "name" : "Keyboard", "stock" : 75, "tags" : ["electronics", "accessory"], "specs" : { "layout" : "US" } },
      { "name" : "Monitor", "stock" : 25, "tags" : ["electronics"], "specs" : { "size_inch" : 27, "resolution" : "4K" } }
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
output "ex1_store_location" {
  description = "Example 1: Extracts the 'store_location' field."
  value       = provider::pyvider::pyvider_jq(local.sample_data_for_func, ".store_location")
}

# ===================================================================
# Example 2: Array Indexing (Result is a primitive)
# ===================================================================
output "ex2_first_item_name" {
  description = "Example 2: Extracts the name of the first item in the 'items' array."
  value       = provider::pyvider::pyvider_jq(local.sample_data_for_func, ".items[0].name")
}

# ===================================================================
# Example 3: Array Projection (Result is a list, needs jsondecode)
# ===================================================================
output "ex3_all_item_names" {
  description = "Example 3: Creates a new array containing only the names of all items."
  value       = jsondecode(provider::pyvider::pyvider_jq(local.sample_data_for_func, "[.items[].name]"))
}

# ===================================================================
# Example 4: Filtering an Array (Result is a list of objects, needs jsondecode)
# ===================================================================
output "ex4_accessory_items" {
  description = "Example 4: Filters for items tagged as 'accessory'."
  value       = jsondecode(provider::pyvider::pyvider_jq(local.sample_data_for_func, ".items[] | select(.tags[] == \"accessory\")"))
}

# ===================================================================
# Example 5: Filtering and Projecting (Result is a list, needs jsondecode)
# ===================================================================
output "ex5_accessory_names" {
  description = "Example 5: Filters for 'accessory' items and returns only their names."
  value       = jsondecode(provider::pyvider::pyvider_jq(local.sample_data_for_func, ".items[] | select(.tags[] == \"accessory\") | .name"))
}

# ===================================================================
# Example 6: Creating a New Object (Result is an object, needs jsondecode)
# ===================================================================
output "ex6_stock_report" {
  description = "Example 6: Creates a custom stock report object."
  value = jsondecode(provider::pyvider::pyvider_jq(
    local.sample_data_for_func,
    "{ report_date: .last_updated, inventory: [ .items[] | { item: .name, quantity: .stock, is_electronic: (.tags[] | contains(\"electronics\")) } ] }"
  ))
}

# ===================================================================
# Example 7: Complex Filtering (Result is a list of objects, needs jsondecode)
# ===================================================================
output "ex7_urgent_restock_items" {
  description = "Example 7: Finds items on sale with stock less than 20."
  value       = jsondecode(provider::pyvider::pyvider_jq(local.sample_data_for_func, ".items[] | select((.tags[] == \"sale\") and .stock < 20)"))
}

# ===================================================================
# Example 8: Using the `jq` Data Source
# Description: This block defines the data source that was failing.
#              It correctly provides the required 'json_input' and 'query' arguments.
# ===================================================================
data "pyvider_jq" "get_active_admins" {
  json_input = local.sample_json_string_for_ds
  query      = ".users[] | select(.active == true and (.roles[] | contains(\"admin\"))) | .name"
}

output "ex8_active_admin_from_ds" {
  description = "Example 8: Result from the pyvider_jq data source."
  # The data source returns a string. Since the query result is a primitive ("Alice"),
  # we do not need jsondecode() here. If the query returned a list or object, we would.
  value = data.pyvider_jq.get_active_admins.result
}