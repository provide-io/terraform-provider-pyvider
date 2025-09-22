terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.0.5"
    }
  }
}

provider "pyvider" {}

resource "pyvider_file_content" "test" {
  path    = "/tmp/test-pyvider.txt"
  content = "Testing Pyvider v0.0.5"
}

data "pyvider_env_variables" "user" {
  keys = ["USER"]
}

output "current_user" {
  value = data.pyvider_env_variables.user.values["USER"]
}
