
# Create file
resource "pyvider_file_content" "test_create" {
  filename = "/tmp/pyvider_test_create.txt"
  content  = "This is a test file created by Pyvider"
}

# Update file (in a separate apply)
resource "pyvider_file_content" "test_update" {
  filename = "/tmp/pyvider_test_update.txt"
  content  = "Initial content"
}

# Read the file using local_file to verify
data "local_file" "verify_create" {
  filename   = pyvider_file_content.test_create.filename
  depends_on = [pyvider_file_content.test_create]
}

output "created_file" {
  value = {
    filename     = pyvider_file_content.test_create.filename
    content      = pyvider_file_content.test_create.content
    exists       = pyvider_file_content.test_create.exists
    content_hash = pyvider_file_content.test_create.content_hash
  }
}

output "verification" {
  value = {
    file_content = data.local_file.verify_create.content
    matches      = data.local_file.verify_create.content == pyvider_file_content.test_create.content
  }
}

# Run apply, then modify the content and run apply again to test updates
output "update_instructions" {
  value = "To test update: Change 'test_update' resource content to 'Updated content' and apply again"
}