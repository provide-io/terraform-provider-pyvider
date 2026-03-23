terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "~> 0.3"
    }
  }
}

provider "pyvider" {
}

data "pyvider_env_variables" "test_env" {
  keys = ["PATH"]
}

output "environment_path" {
  value     = lookup(data.pyvider_env_variables.test_env.values, "PATH", "not_found")
  sensitive = false
}
