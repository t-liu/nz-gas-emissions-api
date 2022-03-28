variable "name" {
  description = "the name of your stack, e.g. \"demo\""
}

variable "route53_zone_id" {
  description = "hosted zone id of route 53"
}

variable "alb_zone_id" {
  description = "zone id of the application load balancer"
}

variable "alb_dns_name" {
  description = "dns name of the application load balancer"
}