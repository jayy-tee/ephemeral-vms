resource "aws_dynamodb_table" "agent_table" {
  name           = "${var.stack_name}-azdevops-agents"
  billing_mode   = "PROVISIONED"
  write_capacity = 5
  read_capacity  = 5
  hash_key       = "Instance-Id"

  attribute {
    name = "Instance-Id"
    type = "S"
  }
}