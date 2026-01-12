# Statistical aggregations and analysis

locals {
  aggregations_response_times_ms = [45, 52, 48, 51, 150, 47, 49, 53, 46, 50]

  # Basic statistics
  aggregations_total_time = provider::pyvider::sum(local.aggregations_response_times_ms)
  aggregations_count = length(local.aggregations_response_times_ms)
  aggregations_average = provider::pyvider::divide(local.aggregations_total_time, local.aggregations_count)

  # Find outliers
  aggregations_min_time = provider::pyvider::min(local.aggregations_response_times_ms)
  aggregations_max_time = provider::pyvider::max(local.aggregations_response_times_ms)
  aggregations_range = provider::pyvider::subtract(local.aggregations_max_time, local.aggregations_min_time)

  # Performance analysis
  aggregations_acceptable_threshold = 100
  aggregations_slow_requests = [for t in local.aggregations_response_times_ms : t if t > local.aggregations_acceptable_threshold]
  aggregations_performance_score = provider::pyvider::multiply(
    provider::pyvider::divide(
      provider::pyvider::subtract(local.aggregations_count, length(local.aggregations_slow_requests)),
      local.aggregations_count
    ),
    100
  )
}

# Budget allocation example
locals {
  aggregations_department_budgets = [50000, 75000, 100000, 125000, 80000]

  aggregations_total_budget = provider::pyvider::sum(local.aggregations_department_budgets)
  aggregations_average_budget = provider::pyvider::divide(local.aggregations_total_budget, length(local.aggregations_department_budgets))

  # Calculate percentages
  aggregations_budget_percentages = [
    for budget in local.aggregations_department_budgets :
    provider::pyvider::round(
      provider::pyvider::multiply(
        provider::pyvider::divide(budget, local.aggregations_total_budget),
        100
      ),
      2
    )
  ]
}

output "aggregations_average" {
  value = {
    performance_metrics = {
      average_response = local.aggregations_average
      min_response = local.aggregations_min_time
      max_response = local.aggregations_max_time
      range = local.aggregations_range
      slow_count = length(local.aggregations_slow_requests)
      performance_score = local.aggregations_performance_score
    }
    budget_analysis = {
      total = local.aggregations_total_budget
      average = local.aggregations_average_budget
      percentages = local.aggregations_budget_percentages
    }
  }
}
