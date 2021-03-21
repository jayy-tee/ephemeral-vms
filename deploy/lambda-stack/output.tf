output "notification_topic_arn" {
  value = aws_sns_topic.autoscale_notifications.arn
}

output "launch_scripts_bucket_name" {
  value = aws_s3_bucket.launchscripts.id
}