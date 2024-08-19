variable "alarm_after_n_minutes_without_success" {
  description = "The number of minutes with no success before triggering the alarm"
  type = number
}

resource "aws_cloudwatch_metric_alarm" "success_metric_alarm" {
  count = var.environment == "prod" ? 1 : 0
  alarm_name          = "${var.app_ident}-failure"
  alarm_description   = "Alarm when ${var.app_ident} is failing"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  datapoints_to_alarm = 1 # Alarm if we saw at least n failures in the evaluation periods
  threshold           = 0
  alarm_actions       = [data.aws_sns_topic.sns_topic.arn]  # Assuming you have an SNS topic for alerts
  treat_missing_data  = "notBreaching"

  metric_query {
    id = "e2"
    metric {
      namespace   = "AWS/Lambda"
      metric_name = "Errors"
      period      = 60  # Set the period to 1 minute (60 seconds)
      stat        = "Sum"
      unit        = "Count"
      dimensions = {
        "FunctionName" = aws_lambda_function.lambda_function.function_name
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
