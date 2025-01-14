variable "app_name" {
  type = string
}

variable "lambda_iam_role" {
  type = string
}

variable "region" {
  type = string
}

variable "lambda_follow_repository_url" {
  type = string
}

variable "lambda_post_repository_url" {
  type = string
}

variable "image_digest_follow" {
  type = string
}

variable "image_digest_post" {
  type = string
}
