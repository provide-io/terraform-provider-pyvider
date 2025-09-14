terraform {
  required_version = ">= 1.0"
  required_providers {
    pyvider = {
      source  = "registry.terraform.io/provide-io/pyvider"
      version = "~> 0.0.5"
    }
  }
}

# String manipulation functions
locals {
  # String manipulation
  original_text = "Hello, Pyvider World!"
  upper_text    = provider::pyvider::upper(local.original_text)
  lower_text    = provider::pyvider::lower(local.original_text)
  reversed_text = provider::pyvider::reverse(local.original_text)
  
  # Replace function
  replaced_text = provider::pyvider::replace(local.original_text, "Pyvider", "Terraform")
  
  # Numeric functions
  numbers = [1, 2, 3, 4, 5]
  sum     = provider::pyvider::sum(local.numbers)
  mean    = provider::pyvider::mean(local.numbers)
  
  # Collection functions
  list1 = ["a", "b", "c"]
  list2 = ["d", "e", "f"]
  concatenated = provider::pyvider::concatenate(local.list1, local.list2)
  
  # Type conversion
  string_number = "42"
  converted_int = provider::pyvider::to_int(local.string_number)
  
  # JQ lens function (if available)
  json_data = jsonencode({
    users = [
      { name = "Alice", age = 30 },
      { name = "Bob", age = 25 }
    ]
  })
  # Extract names using JQ
  user_names = provider::pyvider::lens_jq(local.json_data, ".users[].name")
}

# Create a file with function results
resource "pyvider_file_content" "functions_output" {
  filename = "${path.module}/function_results.json"
  content = jsonencode({
    string_functions = {
      original = local.original_text
      upper    = local.upper_text
      lower    = local.lower_text
      reversed = local.reversed_text
      replaced = local.replaced_text
    }
    numeric_functions = {
      numbers = local.numbers
      sum     = local.sum
      mean    = local.mean
    }
    collection_functions = {
      list1        = local.list1
      list2        = local.list2
      concatenated = local.concatenated
    }
    type_conversion = {
      string_input = local.string_number
      int_output   = local.converted_int
    }
    jq_results = {
      input      = jsondecode(local.json_data)
      user_names = local.user_names
    }
  })
}

# Outputs
output "function_results" {
  description = "All function results"
  value = {
    strings = {
      upper    = local.upper_text
      lower    = local.lower_text
      reversed = local.reversed_text
      replaced = local.replaced_text
    }
    numbers = {
      sum  = local.sum
      mean = local.mean
    }
    collections = {
      concatenated = local.concatenated
    }
    jq = {
      user_names = local.user_names
    }
  }
}

output "results_file" {
  description = "Path to the results file"
  value       = pyvider_file_content.functions_output.filename
}