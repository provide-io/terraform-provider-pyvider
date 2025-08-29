# Example data to query
locals {
  example_data = {
    users = [
      { name = "Alice", age = 30, role = "admin" },
      { name = "Bob", age = 25, role = "user" },
      { name = "Charlie", age = 35, role = "admin" }
    ]
    projects = [
      { id = 1, name = "Project A", status = "active" },
      { id = 2, name = "Project B", status = "completed" },
      { id = 3, name = "Project C", status = "active" }
    ]
  }
}

# Filter users by role
data "pyvider_lens_jq" "admin_users" {
  json_input = jsonencode(local.example_data)
  query      = ".users | map(select(.role == \"admin\")) | map(.name)"
}

# Get active project count
data "pyvider_lens_jq" "active_projects" {
  json_input = jsonencode(local.example_data.projects)
  query      = "map(select(.status == \"active\")) | length"
}

# Complex transformation
data "pyvider_lens_jq" "summary" {
  json_input = jsonencode(local.example_data)
  query      = <<-EOQ
    {
      total_users: .users | length,
      admin_count: .users | map(select(.role == "admin")) | length,
      average_age: .users | map(.age) | add / length,
      active_projects: .projects | map(select(.status == "active")) | map(.name)
    }
  EOQ
}

output "admin_names" {
  description = "Names of admin users"
  value       = data.pyvider_lens_jq.admin_users.result
}

output "active_project_count" {
  description = "Number of active projects"
  value       = data.pyvider_lens_jq.active_projects.result
}

output "summary_report" {
  description = "Summary statistics"
  value       = data.pyvider_lens_jq.summary.result
}
