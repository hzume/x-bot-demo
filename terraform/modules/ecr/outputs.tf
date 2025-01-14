output "lambda_follow_repository_url" {
  description = "The URL of the lambda image repository."
  value       = aws_ecr_repository.repository_follow.repository_url
}

output "lambda_post_repository_url" {
  description = "The URL of the lambda image repository."
  value       = aws_ecr_repository.repository_post.repository_url
}