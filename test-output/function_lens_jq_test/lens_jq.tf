locals {
  inventory_data = {
    items = [
      { "name" : "Laptop", "stock" : 15, "price" : 999.99 },
      { "name" : "Mouse", "stock" : 150, "price" : 29.99 },
      { "name" : "Keyboard", "stock" : 75, "price" : 79.99 },
      { "name" : "Monitor", "stock" : 8, "price" : 299.99 }
    ]
  }
}

# Extract item names
output "item_names" {
  description = "List of all item names"
  value       = provider::pyvider::lens_jq(local.inventory_data, "[.items[].name]")
}

# Filter items with low stock (< 20)
output "low_stock_items" {
  description = "Items with stock below 20"
  value       = provider::pyvider::lens_jq(local.inventory_data, "[.items[] | select(.stock < 20) | .name]")
}

# Calculate total inventory value
output "total_value" {
  description = "Total value of all inventory"
  value       = provider::pyvider::lens_jq(local.inventory_data, ".items | map(.stock * .price) | add")
}

# Get summary statistics
output "inventory_summary" {
  description = "Summary statistics of inventory"
  value = provider::pyvider::lens_jq(local.inventory_data, <<-EOQ
    {
      total_items: .items | length,
      total_stock: .items | map(.stock) | add,
      average_price: .items | map(.price) | add / length,
      most_stocked: .items | max_by(.stock) | .name
    }
  EOQ
  )
}
