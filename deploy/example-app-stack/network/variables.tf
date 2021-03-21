variable "vpc_cidr" {
  type        = string
  description = "CIDR for VPC"
}
variable "environment" {
  type        = string
  description = "Environment name"
}

variable "stack_name" {
  type        = string
  description = "A name for the stack"
}