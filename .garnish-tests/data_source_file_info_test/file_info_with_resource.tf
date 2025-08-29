# File info with file_content resource integration
resource "pyvider_file_content" "data_file" {
  filename = "${path.module}/data.json"
  content = jsonencode({
    timestamp = timestamp()
    data      = var.data_content
  })
}

data "pyvider_file_info" "created_file" {
  path = pyvider_file_content.data_file.filename
  
  depends_on = [pyvider_file_content.data_file]
}

variable "data_content" {
  description = "Content to write to the data file"
  type        = map(string)
  default = {
    key1 = "value1"
    key2 = "value2"
  }
}

output "created_file_size" {
  description = "Size of the created file"
  value       = data.pyvider_file_info.created_file.size
}

output "created_file_hash" {
  description = "Hash from the resource"
  value       = pyvider_file_content.data_file.content_hash
}