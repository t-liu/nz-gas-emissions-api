resource "aws_ssm_parameter" "application_secrets" {
  for_each = var.application-secrets
  name     = each.key
  type     = "SecureString"
  value    = each.value

  tags = {
    Environment = var.environment
  }
}

# arn:aws:ssm::454837591129:parameter/

/*
locals {
  secretsArn = zipmap(keys(var.application-secrets), aws_ssm_parameter.application_secrets.*.name)

  secretMap = [for secretKey in keys(var.application-secrets) : {
    name      = secretKey
    valueFrom = lookup(local.secrets, secretKey)
    }

  ]
}

output "application_secrets_arn" {
  value = aws_ssm_parameter.application_secrets.*.name
}

output "secrets_map" {
  value = local.secretMap
}
*/