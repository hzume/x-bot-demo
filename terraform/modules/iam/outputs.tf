output "lambda_iam_role" {
  value = aws_iam_role.lambda_role.arn
}

output "event_bridge_iam_role" {
  value = aws_iam_role.event_bridge_role.arn
}