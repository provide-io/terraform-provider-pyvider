resource "pyvider_secret_note" "example" {
  # Configuration options here
}

output "example_id" {
  description = "The ID of the pyvider_secret_note resource"
  value       = pyvider_secret_note.example.id
}
