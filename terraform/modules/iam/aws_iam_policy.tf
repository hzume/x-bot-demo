resource "aws_iam_policy" "lambda_policy" {
  name = "${var.app_name}-lambda-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ecr:*",
          "secretsmanager:GetSecretValue"
        ],
        Resource = "*",
        Effect   = "Allow"
      }
    ]
  })
}

resource "aws_iam_policy" "event_bridge_policy" {
  name = "${var.app_name}-event-bridge-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = ["lambda:InvokeFunction"],
        Resource = [var.lambda_function_arn_follow, var.lambda_function_arn_post],
        Effect   = "Allow"
      }
    ]
  })
}
