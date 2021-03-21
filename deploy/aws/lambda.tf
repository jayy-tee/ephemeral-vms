locals {
  lambda_function_name = "${var.stack_name}-agent-deregistration-handler"
  table_name           = "${var.stack_name}-azdevops-agents"
}

resource "aws_s3_bucket" "lambda" {
  bucket = "${local.lambda_function_name}-deploy"
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "lambda_private_access" {
  bucket                  = aws_s3_bucket.lambda.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_object" "lambda_deployment" {
  bucket = aws_s3_bucket.lambda.id
  key    = "deployment-package.zip"
  source = "../../lambda/deployment-package.zip"
  etag   = filemd5("../../lambda/deployment-package.zip")
}

resource "aws_lambda_function" "agent_lambda" {
  function_name    = local.lambda_function_name
  role             = aws_iam_role.iam_for_lambda.arn
  runtime          = "python3.8"
  handler          = "autoscaling_handler.lambda_handler"
  s3_bucket        = aws_s3_bucket.lambda.id
  s3_key           = aws_s3_bucket_object.lambda_deployment.key
  source_code_hash = filebase64sha256("../../lambda/deployment-package.zip")
  timeout          = 15

  environment {
    variables = {
      AGENT_TABLE_NAME = local.table_name
    }
  }

  depends_on = [
    aws_s3_bucket_object.lambda_deployment,
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.lambda_logs,
  ]
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.lambda_function_name}"
  retention_in_days = 3
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "${var.stack_name}-agent-degistration-lambda-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  inline_policy {
    name = "Allow-EC2-Read"
    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : "ec2:Describe*",
          "Resource" : "*"
        }
      ]
    })
  }

  inline_policy {
    name = "Allow-DynamoDb-Access"
    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : "dynamodb:*",
          "Resource" : "arn:aws:dynamodb:*:${data.aws_caller_identity.current.account_id}:table/${aws_dynamodb_table.agent_table.name}"
        }
      ]
    })
  }

  inline_policy {
    name = "Allow-SSM-Parameter-Read"
    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "ssm:GetParametersByPath",
            "ssm:GetParameters",
            "ssm:GetParameter"
          ],
          "Resource" : [
            "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter/azdevops*",
          ]
        }
      ]
    })
  }

}

# See also the following AWS managed policy: AWSLambdaBasicExecutionRole
resource "aws_iam_policy" "lambda_logging" {
  name        = "${var.stack_name}-agent-degistration-lambda"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_lambda_permission" "sns" {
  action        = "lambda:InvokeFunction"
  function_name = local.lambda_function_name
  principal     = "sns.amazonaws.com"
  statement_id  = "AllowSubscriptionToSNS"
  source_arn    = aws_sns_topic.autoscale_notifications.arn
}

resource "aws_sns_topic_subscription" "subscription" {
  endpoint  = aws_lambda_function.agent_lambda.arn
  protocol  = "lambda"
  topic_arn = aws_sns_topic.autoscale_notifications.arn
}
