variable "name" {
  description = "the name of your stack, e.g. \"demo\""
}

variable "environment" {
  description = "the name of your environment, e.g. \"prod\""
}

variable "vpc_id" {
  description = "vpc id from vpc module"
}

variable "container_port" {
  description = "ingress and egress port of the container"
}

variable "rds_mysql_port" {
  description = "ingress and egress port of the rds mysql db"
}