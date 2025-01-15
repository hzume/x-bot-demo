variable "app_name" {
  description = "application name"
  type        = string
}

variable "secret_name" {
  type = string
}

variable "image_tag" {
  type = string
  default = "latest"
}

variable "region" {
  description = "AWS region to create resources in"
  type        = string
}

variable "schedule_expression_follow" {
  type = string
}

variable "schedule_expression_post" {
  type = string
}
