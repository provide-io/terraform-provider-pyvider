locals {
  pluralize_item = "apple"
  pluralize_singular = provider::pyvider::pluralize(local.pluralize_item, 1)  # "apple"
  pluralize_plural = provider::pyvider::pluralize(local.pluralize_item, 2)    # "apples"
  pluralize_custom = provider::pyvider::pluralize("person", 2, "people")  # "people"
}

output "pluralize_plural" {
  value = {
    singular = local.pluralize_singular
    plural   = local.pluralize_plural
    custom   = local.pluralize_custom
  }
}
