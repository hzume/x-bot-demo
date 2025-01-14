variable "app_name" {
  type = string
}

variable "event_bridge_iam_role" {
  type = string
}

variable "lambda_function_arn_follow" {
  type = string
}

variable "lambda_function_arn_post" {
  type = string
}

variable "schedule_expression_follow" {
  type = string
}

variable "schedule_expression_post" {
  type = string
}