resource "aws_ecr_repository" "repository_follow" {
  name                 = var.image_name_follow
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.app_name}-repository-follow"
  }
}

resource "aws_ecr_repository" "repository_post" {
  name                 = var.image_name_post
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.app_name}-repository-post"
  }
}