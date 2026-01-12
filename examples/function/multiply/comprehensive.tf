# Basic numeric function examples

# Addition examples
locals {
  comprehensive_simple_add = provider::pyvider::add(5, 3)      # Returns: 8
  comprehensive_float_add = provider::pyvider::add(2.5, 1.5)   # Returns: 4
  comprehensive_mixed_add = provider::pyvider::add(10, 2.3)    # Returns: 12.3
}

# Subtraction examples
locals {
  comprehensive_simple_subtract = provider::pyvider::subtract(10, 4)    # Returns: 6
  comprehensive_float_subtract = provider::pyvider::subtract(5.5, 2.1)  # Returns: 3.4
  comprehensive_negative_result = provider::pyvider::subtract(3, 7)     # Returns: -4
}

# Multiplication examples
locals {
  comprehensive_simple_multiply = provider::pyvider::multiply(4, 3)     # Returns: 12
  comprehensive_float_multiply = provider::pyvider::multiply(2.5, 4)    # Returns: 10
  comprehensive_zero_multiply = provider::pyvider::multiply(5, 0)       # Returns: 0
}

# Division examples
locals {
  comprehensive_simple_divide = provider::pyvider::divide(12, 3)        # Returns: 4
  comprehensive_float_divide = provider::pyvider::divide(10, 3)         # Returns: 3.333...
  comprehensive_precise_divide = provider::pyvider::divide(15, 3)       # Returns: 5
}

# List operations
locals {
  comprehensive_numbers = [10, 5, 8, 2, 15]

  comprehensive_list_sum = provider::pyvider::sum(local.comprehensive_numbers)         # Returns: 40
  comprehensive_list_min = provider::pyvider::min(local.comprehensive_numbers)         # Returns: 2
  comprehensive_list_max = provider::pyvider::max(local.comprehensive_numbers)         # Returns: 15
}

# Rounding examples
locals {
  comprehensive_round_to_int = provider::pyvider::round(3.7, 0)         # Returns: 4
  comprehensive_round_to_decimal = provider::pyvider::round(3.14159, 2) # Returns: 3.14
  comprehensive_round_negative = provider::pyvider::round(-2.6, 0)      # Returns: -3
}

# Output results for verification
output "comprehensive_simple_divide" {
  value = {
    addition = {
      simple = local.comprehensive_simple_add
      float = local.comprehensive_float_add
      mixed = local.comprehensive_mixed_add
    }
    subtraction = {
      simple = local.comprehensive_simple_subtract
      float = local.comprehensive_float_subtract
      negative = local.comprehensive_negative_result
    }
    multiplication = {
      simple = local.comprehensive_simple_multiply
      float = local.comprehensive_float_multiply
      zero = local.comprehensive_zero_multiply
    }
    division = {
      simple = local.comprehensive_simple_divide
      float = local.comprehensive_float_divide
      precise = local.comprehensive_precise_divide
    }
    list_operations = {
      sum = local.comprehensive_list_sum
      min = local.comprehensive_list_min
      max = local.comprehensive_list_max
    }
    rounding = {
      to_int = local.comprehensive_round_to_int
      to_decimal = local.comprehensive_round_to_decimal
      negative = local.comprehensive_round_negative
    }
  }
}
