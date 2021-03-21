data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  availability_zones         = data.aws_availability_zones.available.names
  public_subnet_base_netnum  = 0
  private_subnet_base_netnum = 100
  public_subnets             = module.vpc.public_subnets
  public_subnet_cidr_blocks = [
    for availability_zone in local.availability_zones :
    cidrsubnet(var.vpc_cidr, 8, local.public_subnet_base_netnum + index(local.availability_zones, availability_zone))
  ]
  vpc_id = module.vpc.vpc_id

  name = "${var.stack_name}-${var.environment}"
}

module "vpc" {
  source          = "terraform-aws-modules/vpc/aws"
  version         = "2.77.0"
  name            = local.name
  cidr            = var.vpc_cidr
  azs             = local.availability_zones
  public_subnets  = local.public_subnet_cidr_blocks
  private_subnets = []

  enable_dns_hostnames     = true
  enable_dns_support       = true
  enable_ipv6              = false
  enable_nat_gateway       = false
  single_nat_gateway       = true
  enable_s3_endpoint       = false
  enable_dynamodb_endpoint = false

  tags = {
    Environment = var.environment
  }

  vpc_tags = {
    Name = "${local.name}-vpc"
  }
} 