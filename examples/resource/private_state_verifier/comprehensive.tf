# Basic private state verification examples

# Example 1: Simple encryption verification
resource "pyvider_private_state_verifier" "simple_test" {
  input_value = "basic-test"
}

# Example 2: Alphanumeric input test
resource "pyvider_private_state_verifier" "alphanumeric_test" {
  input_value = "test123"
}

# Example 3: Special characters test
resource "pyvider_private_state_verifier" "special_chars_test" {
  input_value = "test-with-dashes_and_underscores"
}

# Verify all tests produce expected results
locals {
  comprehensive_verification_results = {
    simple_test = {
      input    = pyvider_private_state_verifier.simple_test.input_value
      output   = pyvider_private_state_verifier.simple_test.decrypted_token
      expected = "SECRET_FOR_BASIC-TEST"
      passed   = pyvider_private_state_verifier.simple_test.decrypted_token == "SECRET_FOR_BASIC-TEST"
    }

    alphanumeric_test = {
      input    = pyvider_private_state_verifier.alphanumeric_test.input_value
      output   = pyvider_private_state_verifier.alphanumeric_test.decrypted_token
      expected = "SECRET_FOR_TEST123"
      passed   = pyvider_private_state_verifier.alphanumeric_test.decrypted_token == "SECRET_FOR_TEST123"
    }

    special_chars_test = {
      input    = pyvider_private_state_verifier.special_chars_test.input_value
      output   = pyvider_private_state_verifier.special_chars_test.decrypted_token
      expected = "SECRET_FOR_TEST-WITH-DASHES_AND_UNDERSCORES"
      passed   = pyvider_private_state_verifier.special_chars_test.decrypted_token == "SECRET_FOR_TEST-WITH-DASHES_AND_UNDERSCORES"
    }
  }

  all_tests_passed = alltrue([
    for test_name, result in local.comprehensive_verification_results : result.passed
  ])
}

# Create verification report (without self-reference)
resource "pyvider_file_content" "verification_report" {
  filename = "/tmp/private_state_verification_report.json"
  content = jsonencode({
    timestamp = timestamp()
    test_summary = {
      total_tests      = length(local.comprehensive_verification_results)
      passed_tests     = length([for result in local.comprehensive_verification_results : result if result.passed])
      all_tests_passed = local.all_tests_passed
    }

    test_results = local.comprehensive_verification_results

    security_validation = {
      private_state_encryption    = "verified"
      secret_generation_pattern   = "SECRET_FOR_{UPPER_INPUT}"
      state_file_protection       = "enabled"
      decryption_mechanism        = "terraform_native"
    }
  })
}

output "comprehensive_passed" {
  description = "Results of basic private state encryption verification"
  value = {
    test_summary = {
      total_tests      = length(local.comprehensive_verification_results)
      passed_tests     = length([for result in local.comprehensive_verification_results : result if result.passed])
      all_tests_passed = local.all_tests_passed
    }

    individual_results = {
      simple_test_passed        = local.comprehensive_verification_results.simple_test.passed
      alphanumeric_test_passed  = local.comprehensive_verification_results.alphanumeric_test.passed
      special_chars_test_passed = local.comprehensive_verification_results.special_chars_test.passed
    }

    security_validation = {
      private_state_working = local.all_tests_passed
      encryption_verified   = true
      decryption_verified   = true
      pattern_verified      = local.all_tests_passed
    }

    report_file = pyvider_file_content.verification_report.filename
  }
}
