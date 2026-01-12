# Basic collection operations
locals {
  basic_items = ["apple", "banana", "cherry"]
  basic_config = { host = "localhost", port = 8080 }

  basic_count = provider::pyvider::length(local.basic_items)  # 3
  basic_has_apple = provider::pyvider::contains(local.basic_items, "apple")  # true
  basic_port = provider::pyvider::lookup(local.basic_config, "port", 3000)  # 8080
}

output "basic_results" {
  value = {
    count = local.basic_count
    has_apple = local.basic_has_apple
    port = local.basic_port
  }
}
