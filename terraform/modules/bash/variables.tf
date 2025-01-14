variable "region" {
  type = string
}

variable "image_tag" {
  type = string
}

variable "image_name_follow" {
  type = string
}

variable "image_name_post" {
  type = string
}

data "aws_caller_identity" "self" {}
locals {
  account_id = data.aws_caller_identity.self.account_id
}
