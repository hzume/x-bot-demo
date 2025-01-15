resource "aws_lambda_function" "lambda_follow" {
  function_name = "${var.app_name}-lambda-follow"
  package_type  = "Image"
  image_uri     = "${var.lambda_follow_repository_url}@${var.image_digest_follow}"
  description   = "lambda_function"
  role          = var.lambda_iam_role
  publish       = true
  memory_size   = 128
  timeout       = 30
  environment {
    variables = {
      REGION = var.region
      SECRET_NAME = var.secret_name
    }
  }

  tags = {
    Name = "${var.app_name}-lamdba"
  }
}

resource "aws_lambda_function" "lambda_post" {
  function_name = "${var.app_name}-lambda-post"
  package_type  = "Image"
  image_uri     = "${var.lambda_post_repository_url}@${var.image_digest_post}"
  description   = "lambda_function"
  role          = var.lambda_iam_role
  publish       = true
  memory_size   = 128
  timeout       = 30
  environment {
    variables = {
      REGION = var.region
      SECRET_NAME = var.secret_name
    }
  }

  tags = {
    Name = "${var.app_name}-lamdba"
  }
}