provider "aws" {
  shared_credentials_file = "~/.aws/credentials"
  profile                 = "default"
  region                  = var.region
}

data "aws_caller_identity" "current" {}