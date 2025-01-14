resource "aws_cloudwatch_log_group" "lambda_follow" {
  name = "/aws/lambda/${var.app_name}-lambda-follow"
}

resource "aws_cloudwatch_log_group" "lambda_post" {
  name = "/aws/lambda/${var.app_name}-lambda-post"
}
