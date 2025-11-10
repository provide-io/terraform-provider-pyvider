locals {
  lookup_settings = {
    database_host = "db.example.com"
    database_port = 5432
  }
  lookup_db_host = provider::pyvider::lookup(local.lookup_settings, "database_host", "localhost")
  lookup_missing = provider::pyvider::lookup(local.lookup_settings, "missing_key", "default")
}

output "lookup_results" {
  value = {
    found    = local.lookup_db_host
    notfound = local.lookup_missing
  }
}
