ephemeral "pyvider_lease" "example" {
  name = "deploy-lock"

  # The lease file is created when the lease opens and removed when it closes.
  path = "${path.module}/deploy.lease"

  # How long the lease is good for before Terraform must renew it.
  ttl_seconds = 300
}

# Ephemeral values cannot be persisted. Consume them from a write-only
# attribute, a provider block, or another ephemeral resource -- never from an
# output or a normal resource argument.
