terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "~> 0.0.5"
    }
  }
}

provider "pyvider" {}

# Example file content resource
resource "pyvider_file_content" "example" {
  path    = "/tmp/pyvider-example.txt"
  content = "Hello from Pyvider!"
}

# Example environment variables data source
data "pyvider_env_variables" "home" {
  keys = ["HOME", "USER"]
}

output "home_directory" {
  value = data.pyvider_env_variables.home.values["HOME"]
}
