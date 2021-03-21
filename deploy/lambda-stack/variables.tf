variable "region" {
  type        = string
  description = "AWS Region"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "stack_name" {
  type        = string
  description = "A name for the stack"
}

variable "azdevops_environment_name" {
  type = string
}

variable "azdevops_project_name" {
  type = string
}
variable "azdevops_url" {
  type = string
}
variable "azdevops_pat" {
  type      = string
  sensitive = true
}