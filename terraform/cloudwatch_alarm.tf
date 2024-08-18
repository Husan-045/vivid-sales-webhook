variable "alarm_after_n_minutes_without_success" {
  description = "The number of minutes with no success before triggering the alarm"
  type = number
}

resource "aws_cloudwatch_metric_alarm" "success_metric_alarm" {
  count = var.environment == "prod" ? 1 : 0
  alarm_name          = "${var.app_ident}-alarm"
  alarm_description   = "Alarm when ${var.app_ident} does not successfully run often enough"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = var.alarm_after_n_minutes_without_success  # 1 evaluation period per minute
  datapoints_to_alarm = var.alarm_after_n_minutes_without_success  # Alarm if all of the evaluation periods have a sum of 0
  threshold           = 0
  alarm_actions       = [data.aws_sns_topic.sns_topic.arn]
  treat_missing_data  = "breaching"

  metric_query {
    id = "e1"
    metric {
      metric_name = "success"
      namespace   = var.cloudwatch_namespace
      period      = 60  # Set the period to 1 minute (60 seconds)
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        environment = var.environment
      }
    }
    return_data = true
  }
}

variable "sns_topic_name" {
  type = string
}

data "aws_sns_topic" "sns_topic" {
  name = var.sns_topic_name
}
