resource "aws_scheduler_schedule" "lambda_scheduler_follow" {
  name       = "${var.app_name}-lambda-scheduler-follow"

  schedule_expression          = var.schedule_expression_follow
  schedule_expression_timezone = "Asia/Tokyo"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = var.lambda_function_arn_follow
    role_arn = var.event_bridge_iam_role
  }
}


resource "aws_scheduler_schedule" "lambda_scheduler_post" {
  name       = "${var.app_name}-lambda-scheduler-post"

  schedule_expression          = var.schedule_expression_post
  schedule_expression_timezone = "Asia/Tokyo"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = var.lambda_function_arn_post
    role_arn = var.event_bridge_iam_role
  }
}