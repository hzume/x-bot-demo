output "lambda_function_arn_follow" {
  value = aws_lambda_function.lambda_follow.arn
}

output "lambda_function_arn_post" {
  value = aws_lambda_function.lambda_post.arn
}
