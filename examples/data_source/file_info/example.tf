data "pyvider_file_info" "target_file" {
  path = "/tmp/example_file.txt"
}

output "example_data" {
  description = "Data from pyvider_file_info"
  value       = data.pyvider_file_info.target_file
}
