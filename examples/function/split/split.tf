locals {
  split_csv_data = "apple,banana,cherry"
  split_by_comma = provider::pyvider::split(",", local.split_csv_data)
  # ["apple", "banana", "cherry"]
}

output "split_results" {
  value = local.split_by_comma
}
