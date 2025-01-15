resource "null_resource" "build_push_image_follow" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "docker logout ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com"
  }

  provisioner "local-exec" {
    command = "aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com"
  }

  provisioner "local-exec" {
    command = "docker build -t ${var.image_name_follow} --file modules/lambda/src/follow.Dockerfile modules/lambda/src/"
  }

  provisioner "local-exec" {
    command = "docker tag ${var.image_name_follow}:latest ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.image_name_follow}:${var.image_tag}"
  }

  provisioner "local-exec" {
    command = "docker push ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.image_name_follow}:${var.image_tag}"
  }

  provisioner "local-exec" {
    command = "docker inspect --format='{{index .RepoDigests 0}}' ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.image_name_follow}:${var.image_tag} | awk -F@ '{print $2}' | tr -d '\n' > ${path.module}/docker_digest_follow.txt"
  }
}

resource "null_resource" "build_push_image_post" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com"
  }

  provisioner "local-exec" {
    command = "docker build -t ${var.image_name_post} --file modules/lambda/src/post.Dockerfile modules/lambda/src/"
  }

  provisioner "local-exec" {
    command = "docker tag ${var.image_name_post}:latest ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.image_name_post}:${var.image_tag}"
  }

  provisioner "local-exec" {
    command = "docker push ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.image_name_post}:${var.image_tag}"
  }

  provisioner "local-exec" {
    command = "docker inspect --format='{{index .RepoDigests 0}}' ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.image_name_post}:${var.image_tag} | awk -F@ '{print $2}' | tr -d '\n' > ${path.module}/docker_digest_post.txt"
  }
}

data "local_file" "image_digest_follow" {
  filename = "${path.module}/docker_digest_follow.txt"
  depends_on = [null_resource.build_push_image_follow]
}

data "local_file" "image_digest_post" {
  filename = "${path.module}/docker_digest_post.txt"
  depends_on = [null_resource.build_push_image_post]
}