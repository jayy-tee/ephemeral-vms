data "aws_iam_policy_document" "instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${local.name}-instance-profile"
  role = aws_iam_role.ec2_instance_role.name
}

resource "aws_iam_role" "ec2_instance_role" {
  name               = "${local.name}-instance-role"
  assume_role_policy = data.aws_iam_policy_document.instance_assume_role_policy.json

  inline_policy {
    name = "Allow-EC2-Tags-Read"
    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : "ec2:DescribeTags",
          "Resource" : "*"
        }
      ]
    })
  }

  inline_policy {
    name = "Allow-S3-Read"
    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "s3:GetObject",
            "s3:ListBucket"
          ],
          "Resource" : [
            "arn:aws:s3:::${var.launch_scripts_bucket_name}",
            "arn:aws:s3:::${var.launch_scripts_bucket_name}/*"
          ]
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
            "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter/${local.name}*"
          ]
        }
      ]
    })
  }
}