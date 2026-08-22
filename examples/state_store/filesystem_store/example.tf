terraform {
  state_store "pyvider_filesystem_store" {
    provider "pyvider" {}

    # Directory the state files are kept in. Created if it does not exist.
    path = "${path.module}/tfstate"
  }
}
