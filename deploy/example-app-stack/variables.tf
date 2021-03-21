variable "region" {
  type        = string
  description = "AWS Region"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR for VPC"
}

variable "ec2_key_name" {
  type        = string
  description = "Name for the Private Key to be used when creating EC2 Instances"
}

variable "ec2_iam_instance_profile" {
  type        = string
  description = "IAM instance profile to be used when creating EC2 Instances"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "stack_name" {
  type        = string
  description = "A name for the stack"
}

variable "launch_scripts_bucket_name" {
  type        = string
  description = "Name of S3 Bucket that will contain launch scripts"
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

variable "notification_topic_arn" {
  type        = string
  description = "ARN of SNS Topic to be used for Autoscaling Notifications"
}