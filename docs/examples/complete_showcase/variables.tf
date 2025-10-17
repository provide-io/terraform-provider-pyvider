# Variables for the complete showcase example

variable "output_directory" {
  description = "Directory for generated files"
  type        = string
  default     = "/tmp"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "pyvider-showcase"
}
