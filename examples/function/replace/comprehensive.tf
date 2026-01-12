# Basic string manipulation function examples

# Case conversion examples
locals {
  comprehensive_case_original_text = "Hello World"

  comprehensive_uppercase_text = provider::pyvider::upper(local.comprehensive_case_original_text)    # Returns: "HELLO WORLD"
  comprehensive_lowercase_text = provider::pyvider::lower(local.comprehensive_case_original_text)    # Returns: "hello world"
}

# String formatting examples
locals {
  comprehensive_template_string = "Hello, {}! You have {} messages."

  comprehensive_formatted_message = provider::pyvider::format(local.comprehensive_template_string, [
    "Alice",
    5
  ])  # Returns: "Hello, Alice! You have 5 messages."

  # Simple template
  comprehensive_simple_format = provider::pyvider::format("User: {}", [
    "admin"
  ])  # Returns: "User: admin"
}

# String joining examples
locals {
  comprehensive_word_list = ["apple", "banana", "cherry"]

  comprehensive_comma_separated = provider::pyvider::join(", ", local.comprehensive_word_list)     # Returns: "apple, banana, cherry"
  comprehensive_pipe_separated = provider::pyvider::join(" | ", local.comprehensive_word_list)     # Returns: "apple | banana | cherry"
  comprehensive_no_separator = provider::pyvider::join("", local.comprehensive_word_list)          # Returns: "applebananacherry"
}

# String splitting examples
locals {
  comprehensive_csv_data = "apple,banana,cherry,date"

  comprehensive_split_by_comma = provider::pyvider::split(",", local.comprehensive_csv_data)       # Returns: ["apple", "banana", "cherry", "date"]

  # Split with limit
  comprehensive_path_string = "/home/user/documents/file.txt"
  comprehensive_split_path = provider::pyvider::split("/", local.comprehensive_path_string)        # Returns: ["", "home", "user", "documents", "file.txt"]
}

# String replacement examples
locals {
  comprehensive_replacement_original_text = "The quick brown fox jumps over the lazy dog"

  comprehensive_replace_fox = provider::pyvider::replace(local.comprehensive_replacement_original_text, "fox", "cat")    # Returns: "The quick brown cat jumps over the lazy dog"
  comprehensive_replace_spaces = provider::pyvider::replace(local.comprehensive_replacement_original_text, " ", "_")     # Returns: "The_quick_brown_fox_jumps_over_the_lazy_dog"
}

# Combined string operations
locals {
  comprehensive_user_input = "  MiXeD cAsE tExT  "

  # Clean and normalize user input
  comprehensive_cleaned_input = provider::pyvider::lower(
    provider::pyvider::replace(
      provider::pyvider::replace(local.comprehensive_user_input, "  ", " "),  # Remove extra spaces
      " ", "_"                                                   # Replace remaining spaces with underscores
    )
  )  # Returns: "mixed_case_text"

  # Create a filename from user input
  comprehensive_filename = provider::pyvider::format("{}.{}", [
    local.comprehensive_cleaned_input,
    "txt"
  ])  # Returns: "mixed_case_text.txt"
}

# Output results for verification
output "comprehensive_results" {
  value = {
    case_conversion = {
      original = local.comprehensive_case_original_text
      uppercase = local.comprehensive_uppercase_text
      lowercase = local.comprehensive_lowercase_text
    }

    formatting = {
      template = local.comprehensive_template_string
      formatted = local.comprehensive_formatted_message
      simple = local.comprehensive_simple_format
    }

    joining = {
      words = local.comprehensive_word_list
      comma_separated = local.comprehensive_comma_separated
      pipe_separated = local.comprehensive_pipe_separated
      no_separator = local.comprehensive_no_separator
    }

    splitting = {
      csv_original = local.comprehensive_csv_data
      csv_split = local.comprehensive_split_by_comma
      path_original = local.comprehensive_path_string
      path_split = local.comprehensive_split_path
    }

    replacement = {
      original = local.comprehensive_replacement_original_text
      fox_to_cat = local.comprehensive_replace_fox
      spaces_to_underscores = local.comprehensive_replace_spaces
    }

    combined_operations = {
      user_input = local.comprehensive_user_input
      cleaned = local.comprehensive_cleaned_input
      filename = local.comprehensive_filename
    }
  }
}
