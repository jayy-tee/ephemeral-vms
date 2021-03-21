resource "aws_autoscaling_group" "appserver_asg" {
  name                = "${local.name}-appserver-asg"
  vpc_zone_identifier = local.public_subnets
  min_size            = 0
  max_size            = 3

  tag {
    key                 = "AzDevOps-Environment"
    value               = var.azdevops_environment_name
    propagate_at_launch = true
  }
  tag {
    key                 = "AzDevOps-Environment-ResourceTags"
    value               = "web,worker"
    propagate_at_launch = true
  }
  tag {
    key                 = "AzDevOps-Project"
    value               = var.azdevops_project_name
    propagate_at_launch = true
  }

  launch_template {
    id      = aws_launch_template.launchtemplate.id
    version = "$Latest"
  }
}

resource "aws_autoscaling_notification" "asg_notifications" {
  group_names = [
    aws_autoscaling_group.appserver_asg.name
  ]

  notifications = [
    "autoscaling:EC2_INSTANCE_LAUNCH",
    "autoscaling:EC2_INSTANCE_TERMINATE",
  ]

  topic_arn = aws_sns_topic.autoscale_notifications.arn
}

