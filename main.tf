terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.26.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.0.1"
    }
  }
  required_version = ">= 1.1.0"

  cloud {
    organization = "t-liu-production"

    workspaces {
      name = "nz-gas-emissions-api"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source             = "./tf/modules/vpc"
  name               = var.name
  cidr               = var.cidr
  private_subnets    = var.private_subnets
  public_subnets     = var.public_subnets
  availability_zones = var.availability_zones
  environment        = var.environment
}

module "sg" {
  source         = "./tf/modules/sg"
  name           = var.name
  vpc_id         = module.vpc.id
  environment    = var.environment
  container_port = var.container_port
  rds_mysql_port = var.rds_mysql_port
}

module "alb" {
  source              = "./tf/modules/alb"
  name                = var.name
  vpc_id              = module.vpc.id
  subnets             = module.vpc.public_subnets
  environment         = var.environment
  alb_security_groups = [module.sg.alb]
  alb_tls_cert_arn    = var.tsl_certificate_arn
  health_check_path   = var.health_check_path
}

module "ecr" {
  source      = "./tf/modules/ecr"
  name        = var.name
  environment = var.environment
}

module "ssm" {
  source              = "./tf/modules/ssm"
  name                = var.name
  environment         = var.environment
  application-secrets = var.application-secrets
}

module "ecs" {
  source                      = "./tf/modules/ecs"
  name                        = var.name
  environment                 = var.environment
  region                      = var.aws_region
  subnets                     = module.vpc.private_subnets
  aws_alb_target_group_arn    = module.alb.aws_alb_target_group_arn
  ecs_service_security_groups = [module.sg.ecs_tasks]
  container_port              = var.container_port
  container_cpu               = var.container_cpu
  container_memory            = var.container_memory
  service_desired_count       = var.service_desired_count
  container_environment = [
    { name = "LOG_LEVEL",
    value = "DEBUG" },
    { name = "PORT",
    value = var.container_port }
  ]
  container_image        = module.ecr.aws_ecr_repository_url
  # container_secrets      = module.ssm.secrets_map
  # container_secrets_arns = module.ssm.application_secrets_arn
}

module "route53" {
  source              = "./tf/modules/route53"
  name                = var.name
  route53_zone_id     = var.route53_zone_id
  alb_zone_id         = module.alb.aws_lb_zone_id
  alb_dns_name        = module.alb.aws_lb_dns_name
}