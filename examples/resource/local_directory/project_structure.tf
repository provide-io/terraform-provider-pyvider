# Project scaffolding with directory structure

locals {
  project_structure_project_name = "my-app"
  project_structure_base_path = "/tmp/${local.project_structure_project_name}"

  directories = [
    "src",
    "src/api",
    "src/models",
    "src/services",
    "tests",
    "tests/unit",
    "tests/integration",
    "config",
    "docs"
  ]
}

# Create project directory structure
resource "pyvider_local_directory" "project_dirs" {
  for_each = toset(local.directories)
  path     = "${local.project_structure_base_path}/${each.value}"
}

# Create README files
resource "pyvider_file_content" "readme_main" {
  filename = "${local.project_structure_base_path}/README.md"
  content  = "# ${local.project_structure_project_name}\n\nProject scaffolding created with Pyvider"

  depends_on = [pyvider_local_directory.project_dirs]
}

resource "pyvider_file_content" "readme_src" {
  filename = "${local.project_structure_base_path}/src/README.md"
  content  = "# Source Code\n\nApplication source code"

  depends_on = [pyvider_local_directory.project_dirs]
}

output "project_structure_project_name" {
  value = {
    base_path = local.project_structure_base_path
    directories_created = length(local.directories)
    directory_list = [for d in local.directories : "${local.project_structure_base_path}/${d}"]
  }
}
