variable "name" {
  description = "nz-gas-emissions-api"
}

variable "environment" {
  description = "prod"
}

variable "aws_region" {
  description = "aws region"
  type        = string
  default     = "us-east-1"
}

variable "aws-access-key" {
  type = string
}

variable "aws-secret-key" {
  type = string
}

variable "application-secrets" {
  description = "A map of secrets that is passed into the application. Formatted like ENV_VAR = VALUE"
  type        = map
}

variable "cidr" {
  description = "the CIDR block for the VPC."
  default     = "10.0.0.0/24"
}

variable "private_subnets" {
  description = "a list of CIDRs for private subnets in your VPC, must be set if the cidr variable is defined, needs to have as many elements as there are availability zones"
  default     = ["10.0.0.128/26"]
  #default     = ["10.0.0.0/20", "10.0.32.0/20", "10.0.64.0/20"]
}

variable "public_subnets" {
  description = "a list of CIDRs for public subnets in your VPC, must be set if the cidr variable is defined, needs to have as many elements as there are availability zones"
  default     = ["10.0.0.0/26"]
  #default     = ["10.0.16.0/20", "10.0.48.0/20", "10.0.80.0/20"]
}

variable "availability_zones" {
  description = "a comma-separated list of availability zones, defaults to all AZ of the region, if set to something other than the defaults, both private_subnets and public_subnets have to be defined as well"
  default     = ["us-east-1a", "us-east-1b", "us-east-1d", "us-east-1d", "us-east-1e", "us-east-1f"]
}

variable "service_desired_count" {
  description = "number of tasks running in parallel"
  default     = 2
}

variable "rds_mysql_port" {
  description = "which rds mysql port is exposed"
  default     = 3306
}

variable "container_port" {
  description = "which docker port is exposed"
  default     = 5000
}

variable "container_cpu" {
  description = "number of cpu units used by the task"
  default     = 256
}

variable "container_memory" {
  description = "amount of memory in MB used by the task"
  default     = 512
}

variable "health_check_path" {
  description = "http path for task health check"
  default     = "/health"
}

variable "tsl_certificate_arn" {
  description = "the ARN of the certificate that the ALB uses for https"
}

variable "route53_zone_id" {
  type = string
  description = "hosted zone id of route 53"
}
