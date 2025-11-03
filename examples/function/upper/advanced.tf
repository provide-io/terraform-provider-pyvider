# Advanced string manipulation and chaining

# Email normalization
locals {
  advanced_user_emails = [
    "  JOHN.DOE@EXAMPLE.COM  ",
    "jane.smith@Example.COM",
    "BOB_JONES@example.com"
  ]

  advanced_normalized_emails = [
    for email in local.advanced_user_emails :
    provider::pyvider::lower(
      provider::pyvider::replace(
        provider::pyvider::replace(email, " ", ""),
        "_", "."
      )
    )
  ]
}

# Slug generation for URLs
locals {
  advanced_article_titles = [
    "How to Use Terraform Providers",
    "Advanced Pyvider Patterns!",
    "String Manipulation 101"
  ]

  advanced_article_slugs = [
    for title in local.advanced_article_titles :
    provider::pyvider::to_kebab_case(
      provider::pyvider::replace(
        provider::pyvider::lower(title),
        "[^a-z0-9\\s-]",
        ""
      )
    )
  ]
}

# Template building with multiple formats
locals {
  advanced_user_data = {
    advanced_first_name = "john"
    advanced_last_name = "doe"
    advanced_role = "engineer"
  }

  # Build formatted strings
  advanced_display_name = provider::pyvider::format("{} {}", [
    provider::pyvider::to_camel_case(local.advanced_user_data.advanced_first_name, true),
    provider::pyvider::to_camel_case(local.advanced_user_data.advanced_last_name, true)
  ])

  advanced_username = provider::pyvider::join(".", [
    provider::pyvider::lower(local.advanced_user_data.advanced_first_name),
    provider::pyvider::lower(local.advanced_user_data.advanced_last_name)
  ])

  advanced_role_display = provider::pyvider::upper(local.advanced_user_data.advanced_role)
}

# CSV parsing and transformation
locals {
  advanced_csv_line = "name,email,department,active"
  advanced_parsed_headers = provider::pyvider::split(",", local.advanced_csv_line)

  # Transform to object keys
  advanced_object_keys = [
    for header in local.advanced_parsed_headers :
    provider::pyvider::to_snake_case(header)
  ]
}

# Complex text processing
locals {
  advanced_raw_text = "Product Name: Widget-2000  Price: $99.99  Stock: 50 units"

  # Extract and normalize
  advanced_parts = provider::pyvider::split("  ", local.advanced_raw_text)
  advanced_product_info = provider::pyvider::split(": ", local.advanced_parts[0])
  advanced_product_name = provider::pyvider::replace(
    local.advanced_product_info[1],
    "-",
    "_"
  )
}

output "advanced_results" {
  value = {
    normalized_emails = local.advanced_normalized_emails
    article_slugs = local.advanced_article_slugs
    user_profile = {
      display_name = local.advanced_display_name
      username = local.advanced_username
      role = local.advanced_role_display
    }
    csv_processing = {
      headers = local.advanced_parsed_headers
      transformed_keys = local.advanced_object_keys
    }
    product_processing = {
      product_name = local.advanced_product_name
    }
  }
}
