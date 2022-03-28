resource "aws_route53_record" "www_a" {
  zone_id = var.route53_zone_id
  name    = "${var.name}.thomasliu.click"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "www_aaaa" {
  zone_id = var.route53_zone_id
  name    = "${var.name}.thomasliu.click"
  type    = "AAAA"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}