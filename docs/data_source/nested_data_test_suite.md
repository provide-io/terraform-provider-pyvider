---
page_title: "Data Source: nested_data_test_suite"
description: |-
  Processes and validates complex nested data structures for Terraform provider testing
---

# nested_data_test_suite (Data Source)

> Processes complex nested data structures for testing CTY data handling and validation

The `pyvider_nested_data_processor` data source is designed for testing and validating complex nested data structures within Terraform providers. It processes nested objects, maps, and lists to ensure proper CTY (Cloud Terraform YAML) data type handling and serialization.

## When to Use This

- **Provider testing**: Test complex data structure handling in Terraform providers
- **Data validation**: Validate nested data structures before processing
- **CTY testing**: Test CTY data type conversion and serialization
- **Development workflows**: Debug complex data structures during provider development
- **Integration testing**: Test data flow through provider components

**Anti-patterns (when NOT to use):**
- Production workloads (this is a testing/development tool)
- Simple data structures (use standard data sources)
- Performance-critical applications
- When data validation is not needed

## Quick Start

```terraform
# Test nested data processing
data "pyvider_nested_data_processor" "test" {
  input_data = {
    level1 = {
      level2 = {
        values = ["a", "b", "c"]
        count = 3
      }
    }
  }
}

# Access processed results
output "processed_data" {
  value = data.pyvider_nested_data_processor.test.processed_data
}
```

## Examples

### Basic Usage

```terraform
# Basic nested data processor examples

# Simple nested data processing
data "pyvider_nested_data_processor" "user_profile" {
  input_data = {
    user = {
      id = 123
      name = "Alice Johnson"
      contact = {
        email = "alice@example.com"
        phone = "+1-555-0123"
        address = {
          street = "123 Main St"
          city = "New York"
          state = "NY"
          zipcode = "10001"
        }
      }
      preferences = {
        theme = "dark"
        language = "en"
        notifications = {
          email = true
          sms = false
          push = true
        }
      }
    }
  }

  # Process specific nested fields
  processors = [
    {
      name = "extract_contact_info"
      path = "user.contact"
      operation = "extract"
    },
    {
      name = "format_address"
      path = "user.contact.address"
      operation = "format"
      format_template = "{street}, {city}, {state} {zipcode}"
    },
    {
      name = "notification_summary"
      path = "user.preferences.notifications"
      operation = "summarize"
    }
  ]
}

# Complex nested data transformation
data "pyvider_nested_data_processor" "api_response" {
  input_data = {
    status = "success"
    timestamp = "2024-01-15T10:30:00Z"
    data = {
      users = [
        {
          id = 1
          name = "Alice"
          department = {
            name = "Engineering"
            budget = 500000
            manager = {
              name = "Sarah Wilson"
              email = "sarah@example.com"
            }
          }
          projects = [
            {
              name = "Project Alpha"
              status = "active"
              deadline = "2024-06-01"
              budget = 150000
            },
            {
              name = "Project Beta"
              status = "planning"
              deadline = "2024-08-15"
              budget = 200000
            }
          ]
        },
        {
          id = 2
          name = "Bob"
          department = {
            name = "Marketing"
            budget = 300000
            manager = {
              name = "Mike Chen"
              email = "mike@example.com"
            }
          }
          projects = [
            {
              name = "Campaign X"
              status = "active"
              deadline = "2024-04-30"
              budget = 75000
            }
          ]
        }
      ]
      metadata = {
        total_users = 2
        total_departments = 2
        last_updated = "2024-01-15T09:45:00Z"
      }
    }
  }

  processors = [
    {
      name = "extract_departments"
      path = "data.users[*].department.name"
      operation = "collect"
    },
    {
      name = "calculate_total_budget"
      path = "data.users[*].department.budget"
      operation = "sum"
    },
    {
      name = "extract_managers"
      path = "data.users[*].department.manager"
      operation = "collect"
    },
    {
      name = "active_projects"
      path = "data.users[*].projects[*]"
      operation = "filter"
      filter_condition = "status == 'active'"
    },
    {
      name = "project_budgets"
      path = "data.users[*].projects[*].budget"
      operation = "sum"
    }
  ]
}

# Configuration validation and processing
variable "service_config" {
  type = map(any)
  default = {
    api_server = {
      host = "api.example.com"
      port = 8080
      ssl = {
        enabled = true
        certificate = {
          path = "/etc/ssl/certs/api.crt"
          key_path = "/etc/ssl/private/api.key"
          ca_bundle = "/etc/ssl/certs/ca-bundle.crt"
        }
        protocols = ["TLSv1.2", "TLSv1.3"]
      }
      database = {
        primary = {
          host = "db1.example.com"
          port = 5432
          credentials = {
            username = "api_user"
            password_ref = "vault://secrets/db/password"
          }
          pool = {
            min_connections = 5
            max_connections = 20
            idle_timeout = 300
          }
        }
        replica = {
          host = "db2.example.com"
          port = 5432
          credentials = {
            username = "readonly_user"
            password_ref = "vault://secrets/db/readonly_password"
          }
          pool = {
            min_connections = 2
            max_connections = 10
            idle_timeout = 600
          }
        }
      }
    }
  }
}

data "pyvider_nested_data_processor" "config_analysis" {
  input_data = var.service_config

  processors = [
    {
      name = "ssl_config"
      path = "api_server.ssl"
      operation = "validate"
      validation_rules = [
        "enabled == true",
        "certificate.path != null",
        "certificate.key_path != null"
      ]
    },
    {
      name = "database_endpoints"
      path = "api_server.database.*"
      operation = "collect"
      output_format = "list"
    },
    {
      name = "total_max_connections"
      path = "api_server.database.*.pool.max_connections"
      operation = "sum"
    },
    {
      name = "credential_references"
      path = "api_server.database.*.credentials.password_ref"
      operation = "collect"
    },
    {
      name = "security_summary"
      path = "api_server"
      operation = "analyze"
      analysis_type = "security"
    }
  ]
}

# Log data processing
locals {
  log_data = {
    application_logs = [
      {
        timestamp = "2024-01-15T10:30:15Z"
        level = "INFO"
        component = "auth"
        message = "User login successful"
        context = {
          user_id = 123
          ip_address = "192.168.1.100"
          user_agent = "Mozilla/5.0..."
          session_id = "sess_abc123"
        }
        metrics = {
          response_time_ms = 45
          memory_usage_mb = 128
        }
      },
      {
        timestamp = "2024-01-15T10:31:20Z"
        level = "ERROR"
        component = "database"
        message = "Connection timeout"
        context = {
          database = "primary"
          query = "SELECT * FROM users WHERE id = ?"
          timeout_ms = 5000
        }
        metrics = {
          retry_count = 3
          total_time_ms = 15000
        }
      },
      {
        timestamp = "2024-01-15T10:32:05Z"
        level = "WARN"
        component = "cache"
        message = "Cache miss rate high"
        context = {
          cache_type = "redis"
          miss_rate = 0.85
          total_requests = 1000
        }
        metrics = {
          memory_usage_mb = 512
          hit_rate = 0.15
        }
      }
    ]
  }
}

data "pyvider_nested_data_processor" "log_analysis" {
  input_data = local.log_data

  processors = [
    {
      name = "error_logs"
      path = "application_logs[*]"
      operation = "filter"
      filter_condition = "level == 'ERROR'"
    },
    {
      name = "component_distribution"
      path = "application_logs[*].component"
      operation = "group_count"
    },
    {
      name = "average_response_time"
      path = "application_logs[*].metrics.response_time_ms"
      operation = "average"
      filter_nulls = true
    },
    {
      name = "memory_usage_stats"
      path = "application_logs[*].metrics.memory_usage_mb"
      operation = "statistics"
    },
    {
      name = "user_activities"
      path = "application_logs[*].context"
      operation = "extract"
      extract_fields = ["user_id", "ip_address", "session_id"]
      filter_nulls = true
    }
  ]
}

# E-commerce order processing
locals {
  order_data = {
    orders = [
      {
        id = "order_001"
        customer = {
          id = 123
          name = "Alice Johnson"
          email = "alice@example.com"
          tier = "premium"
          address = {
            billing = {
              street = "123 Main St"
              city = "New York"
              state = "NY"
              country = "USA"
            }
            shipping = {
              street = "456 Oak Ave"
              city = "Boston"
              state = "MA"
              country = "USA"
            }
          }
        }
        items = [
          {
            product_id = "prod_001"
            name = "Premium Widget"
            quantity = 2
            unit_price = 99.99
            category = "electronics"
            taxes = {
              rate = 0.08
              amount = 15.99
            }
          },
          {
            product_id = "prod_002"
            name = "Standard Gadget"
            quantity = 1
            unit_price = 49.99
            category = "electronics"
            taxes = {
              rate = 0.08
              amount = 4.00
            }
          }
        ]
        payment = {
          method = "credit_card"
          card = {
            last_four = "1234"
            type = "visa"
            expiry = "12/26"
          }
          amount = {
            subtotal = 249.97
            tax = 19.99
            shipping = 15.00
            total = 284.96
          }
        }
        status = "confirmed"
      }
    ]
  }
}

data "pyvider_nested_data_processor" "order_analysis" {
  input_data = local.order_data

  processors = [
    {
      name = "customer_tiers"
      path = "orders[*].customer.tier"
      operation = "group_count"
    },
    {
      name = "total_revenue"
      path = "orders[*].payment.amount.total"
      operation = "sum"
    },
    {
      name = "shipping_states"
      path = "orders[*].customer.address.shipping.state"
      operation = "collect"
    },
    {
      name = "product_categories"
      path = "orders[*].items[*].category"
      operation = "group_count"
    },
    {
      name = "average_order_value"
      path = "orders[*].payment.amount.total"
      operation = "average"
    },
    {
      name = "payment_methods"
      path = "orders[*].payment.method"
      operation = "group_count"
    },
    {
      name = "tax_summary"
      path = "orders[*].payment.amount.tax"
      operation = "statistics"
    }
  ]
}

# Create output files with processed data
resource "pyvider_file_content" "user_profile_report" {
  filename = "/tmp/user_profile_analysis.json"
  content = jsonencode({
    original_data = data.pyvider_nested_data_processor.user_profile.input_data
    processed_results = data.pyvider_nested_data_processor.user_profile.processed_data
    processing_summary = data.pyvider_nested_data_processor.user_profile.processing_summary
    generated_at = timestamp()
  })
}

resource "pyvider_file_content" "api_response_report" {
  filename = "/tmp/api_response_analysis.json"
  content = jsonencode({
    departments = data.pyvider_nested_data_processor.api_response.processed_data.extract_departments
    total_budget = data.pyvider_nested_data_processor.api_response.processed_data.calculate_total_budget
    managers = data.pyvider_nested_data_processor.api_response.processed_data.extract_managers
    active_projects = data.pyvider_nested_data_processor.api_response.processed_data.active_projects
    project_budget_total = data.pyvider_nested_data_processor.api_response.processed_data.project_budgets
    processing_summary = data.pyvider_nested_data_processor.api_response.processing_summary
    generated_at = timestamp()
  })
}

resource "pyvider_file_content" "config_analysis_report" {
  filename = "/tmp/config_analysis.json"
  content = jsonencode({
    ssl_validation = data.pyvider_nested_data_processor.config_analysis.processed_data.ssl_config
    database_endpoints = data.pyvider_nested_data_processor.config_analysis.processed_data.database_endpoints
    total_connections = data.pyvider_nested_data_processor.config_analysis.processed_data.total_max_connections
    security_analysis = data.pyvider_nested_data_processor.config_analysis.processed_data.security_summary
    generated_at = timestamp()
  })
}

resource "pyvider_file_content" "log_analysis_report" {
  filename = "/tmp/log_analysis.json"
  content = jsonencode({
    errors = data.pyvider_nested_data_processor.log_analysis.processed_data.error_logs
    component_stats = data.pyvider_nested_data_processor.log_analysis.processed_data.component_distribution
    performance = {
      avg_response_time = data.pyvider_nested_data_processor.log_analysis.processed_data.average_response_time
      memory_stats = data.pyvider_nested_data_processor.log_analysis.processed_data.memory_usage_stats
    }
    user_activities = data.pyvider_nested_data_processor.log_analysis.processed_data.user_activities
    generated_at = timestamp()
  })
}

resource "pyvider_file_content" "order_analysis_report" {
  filename = "/tmp/order_analysis.json"
  content = jsonencode({
    customer_analysis = {
      tiers = data.pyvider_nested_data_processor.order_analysis.processed_data.customer_tiers
      shipping_states = data.pyvider_nested_data_processor.order_analysis.processed_data.shipping_states
    }
    financial_analysis = {
      total_revenue = data.pyvider_nested_data_processor.order_analysis.processed_data.total_revenue
      average_order_value = data.pyvider_nested_data_processor.order_analysis.processed_data.average_order_value
      tax_summary = data.pyvider_nested_data_processor.order_analysis.processed_data.tax_summary
    }
    product_analysis = {
      categories = data.pyvider_nested_data_processor.order_analysis.processed_data.product_categories
    }
    payment_analysis = {
      methods = data.pyvider_nested_data_processor.order_analysis.processed_data.payment_methods
    }
    generated_at = timestamp()
  })
}

# Output processed data summaries
output "nested_data_processing_examples" {
  value = {
    user_profile = {
      processors_run = length(data.pyvider_nested_data_processor.user_profile.processed_data)
      report_file = pyvider_file_content.user_profile_report.filename
    }

    api_response = {
      departments_found = length(data.pyvider_nested_data_processor.api_response.processed_data.extract_departments)
      total_budget = data.pyvider_nested_data_processor.api_response.processed_data.calculate_total_budget
      report_file = pyvider_file_content.api_response_report.filename
    }

    configuration = {
      validation_passed = data.pyvider_nested_data_processor.config_analysis.processed_data.ssl_config.valid
      max_connections = data.pyvider_nested_data_processor.config_analysis.processed_data.total_max_connections
      report_file = pyvider_file_content.config_analysis_report.filename
    }

    log_analysis = {
      error_count = length(data.pyvider_nested_data_processor.log_analysis.processed_data.error_logs)
      components_found = length(keys(data.pyvider_nested_data_processor.log_analysis.processed_data.component_distribution))
      report_file = pyvider_file_content.log_analysis_report.filename
    }

    order_processing = {
      total_revenue = data.pyvider_nested_data_processor.order_analysis.processed_data.total_revenue
      average_order = data.pyvider_nested_data_processor.order_analysis.processed_data.average_order_value
      report_file = pyvider_file_content.order_analysis_report.filename
    }
  }
}
```

### Complex Nested Structures



### Data Validation Testing



### CTY Type Testing



## Schema



## Common Patterns

### Testing Provider Data Flow
```terraform
# Test complex configuration data
data "pyvider_nested_data_processor" "config_test" {
  input_data = {
    database = {
      connections = [
        {
          host = "primary.db.example.com"
          port = 5432
          ssl_config = {
            enabled = true
            cert_path = "/etc/ssl/certs/db.pem"
          }
        },
        {
          host = "replica.db.example.com"
          port = 5432
          ssl_config = {
            enabled = false
            cert_path = null
          }
        }
      ]
    }
  }
}

# Verify processing results
resource "pyvider_file_content" "test_results" {
  filename = "/tmp/nested_data_test.json"
  content  = jsonencode(data.pyvider_nested_data_processor.config_test.processed_data)
}
```

### Validation Testing
```terraform
# Test data structure validation
data "pyvider_nested_data_processor" "validation_test" {
  input_data = {
    users = [
      {
        name = "alice"
        permissions = {
          read = true
          write = true
          admin = false
        }
        metadata = {
          created_at = "2023-01-01T00:00:00Z"
          tags = ["developer", "team-lead"]
        }
      }
    ]
  }
}
```

## Best Practices

### 1. Use for Development and Testing Only
```terraform
# Good - clearly marked as testing
data "pyvider_nested_data_processor" "dev_test" {
  input_data = var.test_data_structure
}
```

### 2. Structure Test Data Clearly
```terraform
variable "test_nested_data" {
  description = "Test data for nested structure validation"
  type = object({
    config = map(any)
    metadata = object({
      version = string
      tags = list(string)
    })
  })
}

data "pyvider_nested_data_processor" "structured_test" {
  input_data = var.test_nested_data
}
```

### 3. Validate Processing Results
```terraform
# Check that processing completed successfully
locals {
  processing_successful = data.pyvider_nested_data_processor.test.data_hash != null
}

resource "pyvider_file_content" "test_status" {
  count = local.processing_successful ? 1 : 0
  filename = "/tmp/test_passed.txt"
  content  = "Nested data processing test passed"
}
```

## Related Components

- [`pyvider_file_content`](../../resources/file_content.md) - Write test results to files
- [`pyvider_env_variables`](../env_variables.md) - Access environment data for testing
- [`lens_jq` function](../../functions/lens_jq.md) - Query and transform nested data