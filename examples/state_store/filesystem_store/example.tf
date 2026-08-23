terraform {
  state_store "pyvider_filesystem_store" {
    provider "pyvider" {}

    # Directory the state files are kept in, relative to the working directory.
    # Created if it does not exist.
    #
    # This has to be a literal. Terraform decodes a `state_store` block with a nil
    # HCL evaluation context, exactly as it does a `backend` block, so `path.module`
    # and every other traversal fail with "Variables may not be used here". State
    # storage is resolved during `init`, before there is a module graph to resolve
    # them against.
    path = "tfstate"
  }
}
