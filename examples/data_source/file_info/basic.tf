# First, create a file to inspect.
resource "pyvider_file_content" "example" {
  filename = "/tmp/file_info_example.txt"
  content  = "This is a test file."
}

# Now, use the data source to get information about the file.
data "pyvider_file_info" "example" {
  path = pyvider_file_content.example.filename
}

output "basic_file_info_example" {
  value = {
    path    = data.pyvider_file_info.example.path
    exists  = data.pyvider_file_info.example.exists
    size    = data.pyvider_file_info.example.size
    is_file = data.pyvider_file_info.example.is_file
  }
}
