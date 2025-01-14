resource "aws_iam_policy_attachment" "lambda_role_attachment" {
  name       = "${var.app_name}-lambda-attach"
  roles      = ["${aws_iam_role.lambda_role.name}"]
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_policy_attachment" "event_bridge_role_attachment" {
  name       = "${var.app_name}-event-bridge-attach"
  roles      = ["${aws_iam_role.event_bridge_role.name}"]
  policy_arn = aws_iam_policy.event_bridge_policy.arn
}