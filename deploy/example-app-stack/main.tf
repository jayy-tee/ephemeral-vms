provider "aws" {
  shared_credentials_file = "~/.aws/credentials"
  profile                 = "default"
  region                  = var.region
}

data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

data "template_file" "instance_launch_userdata" {
  template = file("userdata.sh.tpl")

  vars = {
    bucket_name = var.launch_scripts_bucket_name
  }
}

locals {
  availability_zones         = data.aws_availability_zones.available.names
  public_subnet_base_netnum  = 0
  private_subnet_base_netnum = 100
  public_subnets             = module.vpc.public_subnets
  public_subnet_cidr_blocks  = module.vpc.public_subnets_cidr_blocks
  vpc_id                     = module.vpc.vpc_id

  name = "${var.stack_name}-${var.environment}"
}

module "vpc" {
  source      = "./network"
  stack_name  = var.stack_name
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
}

resource "aws_launch_template" "launchtemplate" {
  name                   = "${local.name}-appserver"
  update_default_version = true

  iam_instance_profile {
    arn = aws_iam_instance_profile.ec2_profile.arn
  }

  image_id      = "ami-06ce513624b435a22"
  instance_type = "t3.micro"
  key_name      = var.ec2_key_name

  monitoring {
    enabled = true
  }

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.appserver_sg.id]
  }

  user_data = base64encode(data.template_file.instance_launch_userdata.rendered)
}