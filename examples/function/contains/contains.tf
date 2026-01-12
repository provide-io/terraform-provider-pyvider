locals {
  contains_fruits = ["apple", "banana", "cherry"]
  contains_has_apple = provider::pyvider::contains(local.contains_fruits, "apple")   # true
  contains_has_grape = provider::pyvider::contains(local.contains_fruits, "grape")   # false
}

output "contains_results" {
  value = {
    has_apple = local.contains_has_apple
    has_grape = local.contains_has_grape
  }
}
