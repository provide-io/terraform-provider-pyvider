# Infrastructure resource calculations

# Calculate EC2 instance costs
locals {
  resource_calculations_instance_type_hourly_cost = {
    "t2.micro"  = 0.0116
    "t2.small"  = 0.023
    "t2.medium" = 0.0464
    "m5.large"  = 0.096
    "m5.xlarge" = 0.192
  }

  instances = [
    { type = "t2.micro", hours = 730 },
    { type = "m5.large", hours = 730 },
    { type = "t2.small", hours = 365 }
  ]

  # Calculate monthly costs
  monthly_costs = [
    for inst in local.instances :
    provider::pyvider::multiply(
      local.resource_calculations_instance_type_hourly_cost[inst.type],
      inst.hours
    )
  ]

  total_monthly_cost = provider::pyvider::sum(local.monthly_costs)
  average_instance_cost = provider::pyvider::divide(local.total_monthly_cost, length(local.instances))
}

# Storage capacity planning
locals {
  resource_calculations_volume_sizes_gb = [100, 250, 500, 1000]

  resource_calculations_total_storage = provider::pyvider::sum(local.resource_calculations_volume_sizes_gb)
  resource_calculations_largest_volume = provider::pyvider::max(local.resource_calculations_volume_sizes_gb)
  resource_calculations_smallest_volume = provider::pyvider::min(local.resource_calculations_volume_sizes_gb)

  # Calculate percentage of total
  resource_calculations_largest_percentage = provider::pyvider::multiply(
    provider::pyvider::divide(local.resource_calculations_largest_volume, local.resource_calculations_total_storage),
    100
  )
}

# Auto-scaling calculations
locals {
  resource_calculations_current_instances = 3
  resource_calculations_target_cpu_percent = 70
  resource_calculations_current_cpu_percent = 85

  # Calculate scaling factor
  resource_calculations_scale_factor = provider::pyvider::divide(local.resource_calculations_current_cpu_percent, local.resource_calculations_target_cpu_percent)

  # Round up desired instances
  resource_calculations_desired_instances = provider::pyvider::round(
    provider::pyvider::multiply(local.resource_calculations_current_instances, local.resource_calculations_scale_factor),
    0
  )

  # Ensure within min/max bounds
  resource_calculations_min_instances = 2
  resource_calculations_max_instances = 10

  resource_calculations_final_instance_count = provider::pyvider::min([
    provider::pyvider::max([local.resource_calculations_desired_instances, local.resource_calculations_min_instances]),
    local.resource_calculations_max_instances
  ])
}

output "resource_calculations_min_instances" {
  value = {
    cost_analysis = {
      total_monthly = local.total_monthly_cost
      average_per_instance = local.average_instance_cost
      individual_costs = local.monthly_costs
    }
    storage_analysis = {
      total_gb = local.resource_calculations_total_storage
      largest_volume = local.resource_calculations_largest_volume
      smallest_volume = local.resource_calculations_smallest_volume
      largest_percentage = local.resource_calculations_largest_percentage
    }
    autoscaling = {
      current = local.resource_calculations_current_instances
      desired = local.resource_calculations_desired_instances
      final = local.resource_calculations_final_instance_count
      scale_factor = local.resource_calculations_scale_factor
    }
  }
}
