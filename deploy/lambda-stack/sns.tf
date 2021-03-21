resource "aws_sns_topic" "autoscale_notifications" {
  name = "${var.stack_name}-autoscale-topic"
}
