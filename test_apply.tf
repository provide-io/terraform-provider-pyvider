terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.3.21"
    }
  }
}

provider "pyvider" {
}

data "pyvider_env_variables" "test" {
  keys = ["PATH"]
}

output "path" {
  value     = lookup(data.pyvider_env_variables.test.values, "PATH", "not_found")
  sensitive = true
}
