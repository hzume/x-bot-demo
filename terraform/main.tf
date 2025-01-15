terraform {
  required_version = "=1.10.3"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "iam" {
  source                     = "./modules/iam"
  app_name                   = var.app_name
  lambda_function_arn_follow = module.lambda.lambda_function_arn_follow
  lambda_function_arn_post   = module.lambda.lambda_function_arn_post
}

# ECR
module "ecr" {
  source            = "./modules/ecr"
  app_name          = var.app_name
  image_name_follow = "${var.app_name}-follow"
  image_name_post   = "${var.app_name}-post"
}

# LAMBDA
module "lambda" {
  source                       = "./modules/lambda"
  app_name                     = var.app_name
  lambda_iam_role              = module.iam.lambda_iam_role
  region                       = var.region
  secret_name                  = var.secret_name
  lambda_follow_repository_url = module.ecr.lambda_follow_repository_url
  lambda_post_repository_url   = module.ecr.lambda_post_repository_url
  image_digest_follow          = module.bash.image_digest_follow
  image_digest_post            = module.bash.image_digest_post
}

# EVENT BRIDGE
module "event_bridge" {
  source                     = "./modules/event_bridge"
  app_name                   = var.app_name
  lambda_function_arn_follow = module.lambda.lambda_function_arn_follow
  lambda_function_arn_post   = module.lambda.lambda_function_arn_post
  event_bridge_iam_role      = module.iam.event_bridge_iam_role
  schedule_expression_follow = var.schedule_expression_follow
  schedule_expression_post   = var.schedule_expression_post
}

module "bash" {
  source            = "./modules/bash"
  image_tag         = var.image_tag
  image_name_follow = "${var.app_name}-follow"
  image_name_post   = "${var.app_name}-post"
  region            = var.region
}
