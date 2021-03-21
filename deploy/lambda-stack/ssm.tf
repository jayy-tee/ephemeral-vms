resource "aws_ssm_parameter" "azdevops_url" {
  name      = "azdevops.url"
  type      = "String"
  value     = var.azdevops_url
  overwrite = true
}

resource "aws_ssm_parameter" "azdevops_pat" {
  name      = "azdevops.agentregistration.token"
  type      = "SecureString"
  value     = var.azdevops_pat
  overwrite = true
}