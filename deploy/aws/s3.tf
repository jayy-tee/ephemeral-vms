resource "aws_s3_bucket" "launchscripts" {
  bucket = "${var.stack_name}-launchscripts"
  acl    = "private"

  tags = {
    Name        = "${var.stack_name} Launch Scripts"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_public_access_block" "launchscript_private_access" {
  bucket                  = aws_s3_bucket.launchscripts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket_object" "launch_scripts" {
  bucket = aws_s3_bucket.launchscripts.id
  key    = "ec2-scripts.zip"
  source = "../../ec2-scripts.zip"
  etag   = filemd5("../../ec2-scripts.zip")
}
