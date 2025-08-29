# Read file information
data "pyvider_file_info" "existing_file" {
  path = var.file_path
}

variable "file_path" {
  description = "Path to the file to inspect"
  type        = string
  default     = "./README.md"
}

output "file_size" {
  description = "Size of the file in bytes"
  value       = data.pyvider_file_info.existing_file.size
}

output "file_exists" {
  description = "Whether the file exists"
  value       = data.pyvider_file_info.existing_file.exists
}

output "file_modified" {
  description = "Last modification time"
  value       = data.pyvider_file_info.existing_file.modified_time
}